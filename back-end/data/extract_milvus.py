from pymilvus import connections, Collection
import pandas as pd

connections.connect(alias="default", uri="YOUR_MILVUS_DOMAIN")

collection = Collection("YOUR_COLLECTION_NAME")
collection.load()

n = collection.num_entities

results = collection.query(
    expr="",
    output_fields=["id","title","description","thumbnail",
                   "author","publisher","publishing_year","num_pages","language","categories","link"
    ],
    limit = n
)

df = pd.DataFrame(results)

df.to_csv("milvus_books.csv", index=False, encoding="utf-8-sig")

print("done")
