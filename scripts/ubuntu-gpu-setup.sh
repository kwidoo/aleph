#!/bin/bash
# ubuntu-gpu-setup.sh

# Install NVIDIA Container Toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Create project directory
mkdir -p ~/vue-project/{src,chroma_data,docs}
cd ~/vue-project

# Download source files
git clone https://github.com/yourusername/ai4.git ./ai4-temp
cp -r ./ai4-temp/src/* ./src/
rm -rf ./ai4-temp

# Docker Compose file
cat > docker-compose.yml << 'EOL'
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - ./chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - CHROMA_SERVER_HOST=0.0.0.0

  rag-server:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./src:/app/src
      - ./docs:/app/docs
    ports:
      - "8001:8001"
    command: >
      bash -c "pip install chromadb langchain-community sentence-transformers pypdf2 fastapi uvicorn continue &&
      python -u src/rag_server.py"
    depends_on:
      - chromadb
      - ollama

volumes:
  ollama_data:
EOL

# Create agents service
cat > docker-compose.agents.yml << 'EOL'
version: '3.8'

services:
  vue-agent:
    build:
      context: ./agents
      dockerfile: Dockerfile.agents
    volumes:
      - ./src:/app/src
      - ./docs:/app/docs
    environment:
      - CONTINUE_API_KEY=your_api_key
    command: ["python", "agent_controller.py"]
EOL

# Create Dockerfile for agents
mkdir -p agents
cat > agents/Dockerfile.agents << 'EOL'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y curl
RUN pip install requests beautifulsoup4 python-dotenv fastapi uvicorn continue

# Copy agent code
COPY ../src/agents/* .

CMD ["python", "-m", "agent_controller"]
EOL

# RAG server script - copy from src folder
cp src/rag_server.py .
cp src/rag_auth.py .

# Download GPU-optimized models
docker compose run ollama ollama pull deepseek-coder:6.7b
docker compose run ollama ollama pull nomic-embed-text
docker compose run ollama ollama pull phind-coder:34b-v2

# Create authentication configuration
mkdir -p config
cat > config/api_keys.json << 'EOL'
{
  "keys": ["your_secure_key"]
}
EOL

# Create verification script
cat > verify-setup.sh << 'EOL'
#!/bin/bash
# verify-setup.sh

# Check core services
echo "=== Service Status ==="
docker compose ps

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
EOL

chmod +x verify-setup.sh

# Start services
docker compose up -d

echo "Setup complete!"
echo "Run ./verify-setup.sh to verify the installation"
