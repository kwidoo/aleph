#!/bin/bash
# hybrid-setup.sh

# On MacBook (client configuration)
SERVER_IP="your_server_ip"  # Replace with A4000 server IP

# Configure Continue.dev for hybrid access
mkdir -p ~/.continue
cat > ~/.continue/config.json << EOL
{
  "models": [
    {
      "title": "Remote DeepSeek",
      "provider": "openai",
      "model": "deepseek-coder",
      "apiBase": "http://${SERVER_IP}:11434/v1"
    }
  ],
  "contextProviders": [
    {
      "name": "http",
      "params": {
        "url": "http://${SERVER_IP}:8001/query",
        "title": "Remote RAG",
        "description": "A4000-powered code retrieval"
      }
    }
  ],
  "embeddingsProvider": {
    "provider": "openai",
    "model": "text-embedding-ada-002",
    "apiBase": "http://${SERVER_IP}:11434/v1"
  }
}
EOL

# Ensure Python virtual environment is used on the server
cat << 'EOL' > ~/server-setup.sh
#!/bin/bash
if [ ! -d "~/.venv" ]; then
  python3.11 -m venv ~/.venv
fi
source ~/.venv/bin/activate
pip install --upgrade pip
pip install chromadb langchain-community sentence-transformers pypdf2 fastapi uvicorn continue
EOL
chmod +x ~/server-setup.sh

# Instructions for server setup
echo "Mac client configured for hybrid setup with server: ${SERVER_IP}"
echo "The following commands need to be run on the A4000 server:"
echo ""
echo "# On A4000 Server (add authentication)"
echo "docker compose stop rag-server"
echo ""
echo "# Create authenticated RAG endpoint"
echo "cat > rag_auth.py << 'EOL'"
echo "from fastapi import FastAPI, Security, HTTPException"
echo "from fastapi.security import APIKeyHeader"
echo "from rag_server import collection  # From previous setup"
echo ""
echo "app = FastAPI()"
echo "API_KEY_NAME = \"X-API-KEY\""
echo "api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)"
echo ""
echo "VALID_API_KEYS = [\"your_secure_key\"]  # Change to secure key"
echo ""
echo "async def validate_api_key(api_key: str = Security(api_key_header)):"
echo "    if api_key not in VALID_API_KEYS:"
echo "        raise HTTPException(status_code=403, detail=\"Invalid API Key\")"
echo "    return api_key"
echo ""
echo "@app.post(\"/query\")"
echo "async def rag_query("
echo "    query: str,"
echo "    api_key: str = Security(validate_api_key)"
echo "):"
echo "    results = collection.query("
echo "        query_texts=[query],"
echo "        n_results=5"
echo "    )"
echo "    return {"
echo "        \"documents\": results[\"documents\"][0],"
echo "        \"metadatas\": results[\"metadatas\"][0]"
echo "    }"
echo "EOL"
echo ""
echo "# Update docker-compose.yml rag-server command:"
echo "# command: uvicorn rag_auth:app --host 0.0.0.0 --port 8001"
echo ""
echo "docker compose up -d rag-server"
