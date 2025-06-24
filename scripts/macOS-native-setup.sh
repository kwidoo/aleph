#!/bin/bash
# macOS-native-setup.sh

# Verify Homebrew
if ! command -v brew >/dev/null; then
  echo "Homebrew is required but not installed. Please install Homebrew from https://brew.sh/"
  exit 1
fi

# Install core dependencies if missing
brew update
for pkg in python@3.11 tree-sitter coreutils; do
  if brew list "$pkg" >/dev/null 2>&1; then
    echo "$pkg already installed"
  else
    brew install "$pkg"
  fi
done

# Install Ollama if missing
if ! command -v ollama >/dev/null; then
  curl -fsSL https://ollama.ai/install.sh | sh
else
  echo "Ollama already installed"
fi

# Download optimized models
ollama pull deepseek-coder:6.7b-q5_k_m
ollama pull nomic-embed-text
ollama pull llama3.1:8b

# Setup Python virtual environment
if [ ! -d "~/ai-env" ]; then
  python3.11 -m venv ~/ai-env
fi
source ~/ai-env/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install chromadb langchain-community sentence-transformers pypdf2 fastapi uvicorn continue

# Ensure Node and npm are available
if ! command -v npm >/dev/null; then
  echo "npm is required but not installed. Please install Node.js first."
  exit 1
fi

# Create project directory
mkdir -p ~/vue-project/{src,docs}
cd ~/vue-project

# Create Vue project
npm create vue@latest . -- --typescript --jsx --router --pinia --eslint --vitest --playwright

# Install additional dependencies
npm install tailwindcss postcss autoprefixer @headlessui/vue @heroicons/vue
npx tailwindcss init -p

# Create RAG indexing script
mkdir -p scripts
cp /Users/0p/Projects/ai4/src/rag_indexer.py scripts/
cp /Users/0p/Projects/ai4/src/docs_indexer.py scripts/

# Create launch script
cat > ~/launch-ai-env.sh << 'EOL'
#!/bin/bash
source ~/ai-env/bin/activate
ollama serve > /dev/null 2>&1 &
python -m http.server 8000 --directory ~/vue-project > /dev/null 2>&1 &
python ~/vue-project/scripts/rag_indexer.py
echo "AI environment ready! Open VSCode and configure Continue.dev"
EOL

chmod +x ~/launch-ai-env.sh

# Copy agent files
mkdir -p ~/vue-project/scripts/agents
cp /Users/0p/Projects/ai4/src/agents/* ~/vue-project/scripts/agents/

# Setup Continue.dev config
mkdir -p ~/.continue
cat > ~/.continue/config.json << EOL
{
  "models": [
    {
      "title": "LocalAI",
      "provider": "openai",
      "model": "deepseek-coder",
      "apiBase": "http://localhost:11434/v1"
    }
  ],
  "contextProviders": [
    {
      "name": "http",
      "params": {
        "url": "http://localhost:8000/query",
        "title": "Local RAG",
        "description": "Local code retrieval"
      }
    }
  ]
}
EOL

# Create agent runner script
cat > ~/vue-project/run_agent.sh << 'EOL'
#!/bin/bash

# Activate environment
source ~/ai-env/bin/activate

# Run agent controller
python -m scripts.agents.agent_controller "$@"
EOL

chmod +x ~/vue-project/run_agent.sh

# VSCode extensions
code --install-extension Continue.continue
code --install-extension Vue.volar
code --install-extension bradlc.vscode-tailwindcss

echo "Setup complete!"
echo "Run ~/launch-ai-env.sh to start the AI environment"
echo "CD to ~/vue-project and run npm run dev to start Vue development server"
