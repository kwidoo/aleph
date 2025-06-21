import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import FastAPI, Request
import uvicorn
import os

app = FastAPI()

# Initialize ChromaDB client
client = chromadb.HttpClient(host="chromadb", port=8000)
embedding_fn = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://ollama:11434"
)

collection = client.get_or_create_collection(
    "codebase",
    embedding_function=embedding_fn
)

def index_documents():
    """Index documents from /app directory"""
    loader = DirectoryLoader("/app", glob="**/*.{vue,ts,js,md,pdf}")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(docs)

    collection.add(
        documents=[doc.page_content for doc in chunks],
        metadatas=[doc.metadata for doc in chunks],
        ids=[f"id_{i}" for i in range(len(chunks))]
    )

    print(f"Indexed {len(chunks)} chunks")

@app.post("/query")
async def query_documents(request: Request):
    """Query the document collection"""
    data = await request.json()
    query = data.get("query", "")
    n_results = data.get("n_results", 5)

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return {
        "documents": results["documents"][0],
        "metadatas": results["metadatas"][0]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    # Only index if collection is empty
    if collection.count() == 0:
        index_documents()

if __name__ == "__main__":
    index_documents()
    print("RAG server ready at http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
