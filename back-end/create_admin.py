from userdb import SessionLocal
from model import AdminInDB
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

admin_username = "admin"
admin_email = "admin@example.com"
admin_password = "Admin@123"

db = SessionLocal()

existing = db.query(AdminInDB).filter(
    (AdminInDB.username == admin_username) | (AdminInDB.email == admin_email)
).first()

if existing:
    print("Admin user already exists.")
else:
    hashed_pw = pwd_context.hash(admin_password)
    new_admin = AdminInDB(
        username=admin_username,
        email=admin_email,
        password=hashed_pw
    )
    db.add(new_admin)
    db.commit()
    print("Admin user created successfully.")

db.close()
