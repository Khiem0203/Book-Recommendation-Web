# Book-Recommendation-Web
Webapp Book Recommendation System using Vector Search and OpenAI Embedding

# To-do

## Create Milvus standalone database to stored all the vectors embedded:
- You can follow this guide: https://milvus.io/docs/v2.0.x/install_standalone-docker.md
- You can install Attu (UI for Milvus Standalone) to easily manage your database: https://milvus.io/docs/v2.0.x/attu_install-docker.md
## Paste your OpenAI API key to these specific files:
- `main.py`
- `embedding_store.py`
## Create a MySQL database
- Store the user, admin and OpenAI usage token data.
## Embedding your dataset then stored vectors on your Milvus collection:
- Using `embedding_store.py` from ./back-end/data/openai/
- You can use mine dataset (Crawl from Fahasa with 10631 books).
- If you want to use your own dataset, change your features from the file.
## Run `main.py` 
- `main.py` used to serve FastAPI routes and application logic
- If you installed Attu, usually it will take port 8000 as default, so to run file `main.py` we use port 8080 or whatever you want
- Paste this to your terminal: uvicorn main:app --host 127.0.0.1 --port 8080
## Front-end and Admin-panel
- Both using React framework.
- cd to each folder seperately then run this on termial: npm start

### For more specific informations, read Readme.md in back-end folder

