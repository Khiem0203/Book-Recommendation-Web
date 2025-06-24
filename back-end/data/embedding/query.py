# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_milvus import Milvus
from pymilvus import connections, Collection
import torch

embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

# This is the local embedding model from HuggingFace, you can try this model to compare with OpenAI embedding model
# embedding_model = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2",
#     model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"}
# )

connections.connect(alias="default", uri="http://127.0.0.1:19530")
collection_name = "books_dataset"
collection = Collection(collection_name)
text_field = "page_content"

vectorstore = Milvus(
    embedding_function=embedding_model,
    connection_args={"uri": "http://127.0.0.1:19530"},
    collection_name=collection_name,
    text_field="page_content"
)

def recommend_books(query: str):
    query_embedding = embedding_model.embed_query(query)

    usage = getattr(embedding_model.client, "last_response", None)
    usage_data = usage.usage if usage and hasattr(usage, "usage") else {}

    results = vectorstore.similarity_search_by_vector(query_embedding, k=1000)
    return {
        "data": [
            {
                "id": doc.id,
                **doc.metadata
            }
            for doc in results
        ],
        "usage": {
            "prompt_tokens": usage_data.get("prompt_tokens", 0),
            "completion_tokens": 0
        } if usage_data else {}
    }

if __name__ == "__main__":
    user_query = "teen"
    top_books = recommend_books(user_query)

    print("\nResult:\n")
    for i, book in enumerate(top_books, 1):
        print(f"{i}. [{book['id']}] {book.get('title')} by {book.get('author')}")