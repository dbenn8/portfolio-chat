# app/weaviate_client.py
from typing import Optional
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery
from app.config import settings

COLLECTION_NAME = "Portfolio"

_client: Optional[weaviate.WeaviateClient] = None


def get_client() -> weaviate.WeaviateClient:
    global _client
    if _client is None or not _client.is_connected():
        _client = weaviate.connect_to_weaviate_cloud(
            cluster_url=settings.weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(settings.weaviate_api_key),
        )
    return _client


def ensure_collection():
    client = get_client()
    if not client.collections.exists(COLLECTION_NAME):
        client.collections.create(
            name=COLLECTION_NAME,
            properties=[
                Property(name="text", data_type=DataType.TEXT),
                Property(name="source", data_type=DataType.TEXT),
                Property(name="project", data_type=DataType.TEXT),
                Property(name="section", data_type=DataType.TEXT),
                Property(name="content_type", data_type=DataType.TEXT),
                Property(name="slug", data_type=DataType.TEXT),
            ],
        )


def chunk_text(text: str, max_tokens: int = 250, overlap_tokens: int = 50) -> list[str]:
    words = text.split()
    if len(words) <= max_tokens:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_tokens
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap_tokens
    return chunks


def upsert_chunks(chunks: list[dict]):
    client = get_client()
    collection = client.collections.get(COLLECTION_NAME)
    with collection.batch.dynamic() as batch:
        for chunk in chunks:
            batch.add_object(
                properties={
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "project": chunk["project"],
                    "section": chunk["section"],
                    "content_type": chunk["content_type"],
                    "slug": chunk.get("slug", ""),
                },
                vector=chunk["vector"],
            )


def search(query_text: str, query_vector: list[float], top_k: int = 5) -> list[dict]:
    client = get_client()
    collection = client.collections.get(COLLECTION_NAME)
    results = collection.query.hybrid(
        query=query_text,
        vector=query_vector,
        limit=top_k,
        alpha=0.5,
        return_metadata=MetadataQuery(score=True),
    )
    return [
        {
            "text": obj.properties["text"],
            "source": obj.properties["source"],
            "project": obj.properties["project"],
            "section": obj.properties["section"],
            "content_type": obj.properties["content_type"],
            "slug": obj.properties.get("slug", ""),
            "score": obj.metadata.score,
        }
        for obj in results.objects
    ]


def clear_collection():
    client = get_client()
    if client.collections.exists(COLLECTION_NAME):
        client.collections.delete(COLLECTION_NAME)
    ensure_collection()
