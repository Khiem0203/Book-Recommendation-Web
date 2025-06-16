# Book Recommendations

## Back-end

This is the backend API for a book recommendation system using FastAPI, MySQL, OpenAI embeddings, and Milvus for vector-based search. Admin features and user authentication are supported via JWT.

Using Dataset crawled from Fahasa (Sorry fahasa), 10631 books with features: id, title, author, description, categories, publisher, publishing_year, num_pages, language, thumbnail and direct link to the website of that book.

## Features
### User
- Register & Login (JWT-based)
- Save favorite books
- View personal favorites
### Book Recommendation System
- Semantic search using OpenAi embeddings
- Recommend books based on vector similarity
- Chatbot: Ask question and get book suggestions (GPT-powered)
- Explanation generator: Give users a reason why they might like the book (GPT-powered)
### Admin panel
- Admin login 
- View & delete users
- Search & delete books in Milvus
- View OpenAI token usage (input/output by purpose)

### File Overview (Which mainly used for this project):
- `main.py`: FastAPI routes and application logic  
- `model.py`: SQLAlchemy models for users, admins, favorites, logs  
- `crud.py`: Database operations (create, read, update, delete)  
- `userdb.py`: MySQL database connection and session setup  
- `embedding_store.py`: Store book embeddings into Milvus  
- `query.py`: Search and recommend books from Milvus  
- `suggest_words.py`: Autocomplete keyword suggestion logic  
- `create_admin.py`: Script to create initial admin account  

### Tech Stack:
- **FastAPI**: Web API framework
- **SQLAlchemy**: ORM for MySQL
- **MySQL**: User & log database
- **Milvus**: Vector similarity search for book embeddings
- **OpenAI**: GPT models for chat & explanation, embedding models
- **Langchain**: Embedding utilities
- **JWT**: Authentication for users and admins


