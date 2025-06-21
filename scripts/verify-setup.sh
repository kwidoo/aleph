#!/bin/bash
# verify-setup.sh

# Check core services
echo "=== Service Status ==="
if [ "$PLATFORM" = "mac" ]; then
    lsof -i :11434 && echo "Ollama: RUNNING"
    lsof -i :8000 && echo "ChromaDB: RUNNING"
elif [ "$PLATFORM" = "ubuntu" ]; then
    docker compose ps
fi

# Test model response
echo -e "\n=== Model Test ==="
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "deepseek-coder",
  "prompt": "// Vue3 component using Composition API"
}' | grep "text"

# Test RAG retrieval
echo -e "\n=== RAG Test ==="
curl -X POST http://localhost:8001/query -H "Content-Type: application/json" -d '{
  "query": "Vue3 component with TypeScript"
}' | jq '.documents[0] | length'
