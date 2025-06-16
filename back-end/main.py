from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from crud import create_user, get_user_by_username_or_email, add_to_favorites, is_favorites, remove_from_favorites
from userdb import get_db, SessionLocal
from model import RegisterUser, User, Favorite, TokenData, UserInDB, FavoriteInDB, AdminInDB
from data.openai.query import recommend_books
from pydantic import BaseModel
from openai import AsyncOpenAI
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from suggest_words import fetch_book_suggestions
from sqlalchemy import or_, text
from pymilvus import connections, Collection
import os
import getpass

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("YOUR_OPENAI_API_KEY")

connections.connect(alias = "default", uri = "YOUR_MILVUS_URL")
milvus_collection = Collection("YOUR_COLLECTION_NAME")
milvus_collection.load()
print(" [FastAPI] Milvus contains:", milvus_collection.num_entities, "vectors")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "YOUR_DOMAIN_URL"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = get_user_by_username_or_email(db, identifier=username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        is_admin = payload.get("admin", False)
        if not username or not is_admin:
            raise HTTPException(status_code=401, detail="Admin token invalid")
    except JWTError:
        raise HTTPException(status_code=401, detail="Admin token invalid")

    admin = db.query(AdminInDB).filter(AdminInDB.username == username).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")
    return admin

@app.post("/register/")
def register_user(user: RegisterUser, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = create_user(db=db, username=user.username, email=user.email, password=hashed_password)
    return {"message": "User created successfully", "user_id": db_user.id}

@app.post("/login/")
def login_user(user: User, db: Session = Depends(get_db)):
    db_user = get_user_by_username_or_email(db=db, identifier=user.identifier)
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/admin/login/")
def login_admin(user: User, db: Session = Depends(get_db)):
    db_admin = db.query(AdminInDB).filter(
        or_(AdminInDB.username == user.identifier, AdminInDB.email == user.identifier)
    ).first()
    if not db_admin or not pwd_context.verify(user.password, db_admin.password):
        raise HTTPException(status_code=400, detail="Invalid admin credentials")
    token = create_access_token(data={"sub": db_admin.username, "admin": True})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/logininfo")
def get_user_info(current_user: UserInDB = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email
    }

@app.get("/admin/overview")
def admin_overview(db: Session = Depends(get_db), current_admin: AdminInDB = Depends(get_current_admin)):
    return {
        "total_users": db.query(UserInDB).count(),
        "total_favorites": db.query(FavoriteInDB).count(),
        "total_books": milvus_collection.num_entities
    }

@app.get("/admin/users")
def list_users(db: Session = Depends(get_db), current_admin: AdminInDB = Depends(get_current_admin)):
    users = db.query(UserInDB).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]

@app.get("/admin/users/search")
def search_users(query: str, db: Session = Depends(get_db), current_admin: AdminInDB = Depends(get_current_admin)):
    users = db.query(UserInDB).filter(
        or_(
            UserInDB.username.ilike(f"%{query}%"),
            UserInDB.email.ilike(f"%{query}%")
        )
    ).all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in users]

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: AdminInDB = Depends(get_current_admin)):
    user = db.query(UserInDB).filter(UserInDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@app.get("/admin/books/count")
def count_books(current_admin: AdminInDB = Depends(get_current_admin)):
    return {"total_books": milvus_collection.num_entities}

@app.get("/admin/books/search")
def search_books(query: str, current_admin: AdminInDB = Depends(get_current_admin)):
    expr = f'title like "%{query}%" or author like "%{query}%" or categories like "%{query}%"'
    try:
        results = milvus_collection.query(
            expr=expr,
            output_fields=["id", "title", "author", "categories"],
            limit=100
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/admin/books/{book_id}")
def delete_book(book_id: str, current_admin: AdminInDB = Depends(get_current_admin)):
    try:
        milvus_collection.delete(expr=f'id == "{book_id}"')
        return {"message": f"Book {book_id} deleted from Milvus"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/is_favorite/{book_id}")
def is_favorite(book_id: str, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    return {"is_favorite": is_favorites(db, current_user.id, book_id)}

@app.post("/favorites/")
def add_favorite(favorite: Favorite, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    db_fav = add_to_favorites(db=db, user_id=current_user.id, book_id=favorite.book_id)
    return {"message": "Book added to favorites"}

@app.get("/userfavorites")
def get_favorites(db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    favorites = db.query(FavoriteInDB).filter(FavoriteInDB.user_id == current_user.id).all()
    books = []
    for fav in favorites:
        result = milvus_collection.query(
            expr=f'id == "{fav.book_id}"',
            output_fields=["id", "title", "author", "publishing_year", "thumbnail",
                           "description", "publisher", "num_pages", "language", "categories", "link"],
            limit=1
        )
        if result:
            books.append(result[0])
    return {"favorites": books}

@app.delete("/favorites/{book_id}")
def delete_favorite(book_id: str, db: Session = Depends(get_db), current_user: UserInDB = Depends(get_current_user)):
    success = remove_from_favorites(db, current_user.id, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not in favorites")
    return {"message": "Removed from favorites"}

@app.get("/bookrcm")
def recommend(query: str = Query(...)):
    try:
        result = recommend_books(query)

        if hasattr(result, "usage"):
            usage = result.usage
            db = SessionLocal()
            db.execute(
                text("INSERT INTO openai_logs (purpose, input_tokens, output_tokens) VALUES (:p, :in_t, :out_t)"),
                {"p": "chatbot", "in_t": usage.prompt_tokens, "out_t": usage.completion_tokens}
            )
            db.commit()
            db.close()

        return {"results": result.data if hasattr(result, "data") else result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/suggestions")
def suggestions(query: str = Query(...)):
    try:
        return {"suggestions": fetch_book_suggestions(query)}
    except Exception as e:
        return {"error": str(e)}

class ExplainRequest(BaseModel):
    title: str
    author: str
    description: str

@app.post("/explain")
async def explain_book(data: ExplainRequest):
    prompt = f"""You're a helpful book recommender.
Title: {data.title}
Author(s): {data.author}
Description: {data.description}
Explain to a reader why they might like this book in 2-3 Vietnamese sentences."""
    try:
        client = AsyncOpenAI()
        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You're a friendly book expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=120
        )
        usage = res.usage
        db = SessionLocal()
        db.execute(
            text("INSERT INTO openai_logs (purpose, input_tokens, output_tokens) VALUES (:p, :in_t, :out_t)"),
            {"p": "chatbot", "in_t": usage.prompt_tokens, "out_t": usage.completion_tokens}
        )
        db.commit()
        db.close()
        return {"reason": res.choices[0].message.content.strip()}
    except Exception as e:
        return {"error": str(e)}

class ChatRequest(BaseModel):
    message: str

@app.post("/chatbot-recommend")
async def chatbot(data: ChatRequest):
    prompt = f"""You're a helpful book recommender. Based on this question from the user:
"{data.message}"
Suggest 1–2 suitable books and explain shortly in Vietnamese. If they have any question from any book or books from you provided, answer them in Vietnamese."""
    try:
        client = AsyncOpenAI()
        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You're a friendly book expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        usage = res.usage
        db = SessionLocal()
        db.execute(
            text("INSERT INTO openai_logs (purpose, input_tokens, output_tokens) VALUES (:p, :in_t, :out_t)"),
            {"p": "chatbot", "in_t": usage.prompt_tokens, "out_t": usage.completion_tokens}
        )
        db.commit()
        db.close()
        return {"reply": res.choices[0].message.content.strip()}
    except Exception as e:
        return {"error": str(e)}

@app.get("/admin/token-usage")
def get_token_usage(db: Session = Depends(get_db), current_admin: AdminInDB = Depends(get_current_admin)):
    rows = db.execute(
        text("SELECT purpose, input_tokens, output_tokens, created_at FROM openai_logs ORDER BY created_at DESC")
    ).fetchall()
    usage_by_purpose = {}
    logs = []

    for row in rows:
        purpose = row[0]
        input_tokens = row[1] or 0
        output_tokens = row[2] or 0
        created_at = row[3]
        logs.append({
            "purpose": purpose,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "created_at": created_at
        })

        if purpose not in usage_by_purpose:
            usage_by_purpose[purpose] = {"input": 0, "output": 0}
        usage_by_purpose[purpose]["input"] += input_tokens
        usage_by_purpose[purpose]["output"] += output_tokens

    total_input = sum(p["input"] for p in usage_by_purpose.values())
    total_output = sum(p["output"] for p in usage_by_purpose.values())

    return {
        "summary": {
            "by_purpose": usage_by_purpose,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output
        },
        "logs": logs
    }
