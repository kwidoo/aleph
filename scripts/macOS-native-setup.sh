#!/bin/bash
# macOS-native-setup.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Install core dependencies
brew update
brew install python@3.11 tree-sitter coreutils

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download optimized models
ollama pull deepseek-coder:6.7b-q5_k_m
ollama pull nomic-embed-text
ollama pull llama3.1:8b

# Setup Python virtual environment
if [ ! -d "$HOME/.venv" ]; then
  python3.11 -m venv "$HOME/.venv"
fi
source "$HOME/.venv/bin/activate"

# Install Python dependencies
pip install --upgrade pip
pip install chromadb langchain-community sentence-transformers pypdf2 fastapi uvicorn continue

# Create project directory
mkdir -p "$HOME/vue-project"
cd "$HOME/vue-project"

read -p "Clone an existing repo into ~/vue-project? [y/N]: " CLONE_CHOICE
if [[ $CLONE_CHOICE =~ ^[Yy]$ ]]; then
  DEFAULT_REPO="https://github.com/yourusername/ai4.git"
  read -p "Repository to clone (press Enter for $DEFAULT_REPO): " REPO_URL
  REPO_URL=${REPO_URL:-$DEFAULT_REPO}
  git clone "$REPO_URL" .
  npm install
else
  npm create vue@latest . -- --typescript --jsx --router --pinia --eslint --vitest --playwright
  npm install tailwindcss postcss autoprefixer @headlessui/vue @heroicons/vue
  npx tailwindcss init -p
fi

# Create RAG indexing script
mkdir -p scripts
cp "$REPO_ROOT/src/rag_indexer.py" scripts/
cp "$REPO_ROOT/src/docs_indexer.py" scripts/

# Create launch script
# Launch script
cat > "$HOME/launch-ai-env.sh" <<'EOL'
#!/bin/bash
source "$HOME/.venv/bin/activate"
ollama serve > /dev/null 2>&1 &
python -m http.server 8000 --directory "$HOME/vue-project" > /dev/null 2>&1 &
python "$HOME/vue-project/scripts/rag_indexer.py"
echo "AI environment ready! Open VSCode and configure Continue.dev"
EOL

chmod +x "$HOME/launch-ai-env.sh"

# Copy agent files
mkdir -p scripts/agents
cp "$REPO_ROOT/src/agents"/* scripts/agents/

# Setup Continue.dev config
mkdir -p "$HOME/.continue"
cat > "$HOME/.continue/config.json" <<'EOL'
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
cat > run_agent.sh <<'EOL'
#!/bin/bash

source "$HOME/.venv/bin/activate"

python -m scripts.agents.agent_controller "$@"
EOL

chmod +x run_agent.sh

# VSCode extensions
code --install-extension Continue.continue
code --install-extension Vue.volar
code --install-extension bradlc.vscode-tailwindcss

echo "Setup complete!"
echo "Run ~/launch-ai-env.sh to start the AI environment"
echo "CD to ~/vue-project and run npm run dev to start Vue development server"
