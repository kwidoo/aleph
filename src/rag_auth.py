from fastapi import FastAPI, Security, HTTPException, Request
from fastapi.security import APIKeyHeader
import uvicorn
import os
from rag_server import collection  # Import collection from main RAG server

app = FastAPI()
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Set this to a secure value in production
VALID_API_KEYS = ["your_secure_key"]

async def validate_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.post("/query")
async def rag_query(
    request: Request,
    api_key: str = Security(validate_api_key)
):
    """Query the RAG system with authentication"""
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
async def health_check(api_key: str = Security(validate_api_key)):
    """Health check endpoint"""
    return {"status": "healthy", "authenticated": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
