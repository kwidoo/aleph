import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import FastAPI, Request
import uvicorn
import os
from knowledge_manager import knowledge_hub
from debug_agent import DebugAgent
from security_agent import SecurityAgent

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

# Initialize agents
debug_agent = DebugAgent()
security_agent = SecurityAgent()

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

@app.get("/task-logs")
def get_task_logs():
    """Fetch task logs."""
    return {"logs": ["Task 1 completed", "Task 2 in progress"]}

@app.get("/performance-metrics")
def get_performance_metrics():
    """Fetch performance metrics."""
    return {"metrics": {"CPU": "75%", "Memory": "60%"}}

@app.get("/audit-results")
def get_audit_results():
    """Fetch audit results."""
    return {"results": ["Audit 1 passed", "Audit 2 failed"]}

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    # Only index if collection is empty
    if collection.count() == 0:
        index_documents()

def initialize_knowledge_hub():
    """Initialize Knowledge Hub on server startup"""
    knowledge_hub.index_resource("https://vuejs.org/guide", "markdown")
    knowledge_hub.index_resource("figma-designs", "designs")

if __name__ == "__main__":
    index_documents()
    initialize_knowledge_hub()
    print("RAG server ready at http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
