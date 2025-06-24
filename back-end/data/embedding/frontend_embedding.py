import os
import pandas as pd
from langchain_core.documents import Document
from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm

embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

def embedding(csv_path: str, collection_name: str = "books_dataset") -> tuple[int, int, int]:
    df = pd.read_csv(csv_path)
    df.fillna({
        "title": "", "description": "", "thumbnail": "", "author": "",
        "publisher": "", "publishing_year": 0, "num_pages": 0,
        "language": "", "categories": "", "link": ""
    }, inplace=True)

    df["publishing_year"] = pd.to_numeric(df["publishing_year"], errors="coerce").fillna(0).astype(int)
    df["num_pages"] = pd.to_numeric(df["num_pages"], errors="coerce").fillna(0).astype(int)
    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype(int)
    df.reset_index(drop=True, inplace=True)

    processed_ids = load_processed_ids("processed_ids.txt")

    vectorstore = Milvus(
        embedding_function=embedding_model,
        connection_args={"uri": "http://127.0.0.1:19530"},
        collection_name=collection_name,
        primary_field="id",
        vector_field="vector",
        text_field="page_content",
        auto_id=False,
        index_params={
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        },
        consistency_level="Strong"
    )

    docs = []
    uploaded_count = 0
    estimated_input_tokens = 0

    with open("processed_ids.txt", "a") as log_file:
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Embedding books"):
            book_id = int(row["id"])
            if book_id in processed_ids:
                continue

            doc = create_document_from_row(row, book_id)
            docs.append(doc)
            estimated_input_tokens += len(doc.page_content.split())

            if len(docs) >= 100:
                upload_batch(vectorstore, docs, log_file)
                uploaded_count += len(docs)
                docs = []

        if docs:
            upload_batch(vectorstore, docs, log_file)
            uploaded_count += len(docs)

    return uploaded_count, estimated_input_tokens, 0


def load_processed_ids(filepath: str) -> set:
    if not os.path.exists(filepath):
        return set()
    with open(filepath, "r") as f:
        return set(int(line.strip()) for line in f.readlines())


def create_document_from_row(row, book_id: int) -> Document:
    content = f"{row['title']} {row['description']} {row['author']} {row['categories']}"
    return Document(
        page_content=content,
        id=book_id,
        metadata={
            "title": row["title"],
            "author": row["author"],
            "description": row["description"],
            "categories": row["categories"],
            "publisher": row["publisher"],
            "publishing_year": row["publishing_year"],
            "num_pages": row["num_pages"],
            "language": row["language"],
            "thumbnail": row["thumbnail"],
            "link": row["link"]
        }
    )

def upload_batch(vectorstore, docs, log_file):
    vectorstore.add_documents(docs, ids=[d.id for d in docs])
    for d in docs:
        log_file.write(f"{d.id}\n")
    log_file.flush()
