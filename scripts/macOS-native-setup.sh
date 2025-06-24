#!/bin/bash
# macOS-native-setup.sh
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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
  brew install ollama
else
  echo "Ollama already installed"
fi

# Ensure Ollama server is running for model downloads
if ! pgrep -f "ollama" >/dev/null; then
  ollama serve > /dev/null 2>&1 &
  sleep 5
fi

# Download optimized models
echo "Downloading optimized models..."
echo "Deepseek Coder 6.7B"
ollama pull deepseek-coder:6.7b-q5_K_M
echo "Nomic embed text"
ollama pull nomic-embed-text
echo "Llama 3.1 8B"
ollama pull llama3.1:8b

# Setup Python virtual environment
if [ ! -d "$HOME/.venv" ]; then
  python3.11 -m venv "$HOME/.venv"
fi
source "$HOME/.venv/bin/activate"

# Install Python dependencies
pip install --upgrade pip
pip install chromadb langchain-community sentence-transformers pypdf2 fastapi uvicorn

# Ensure Node and npm are available
if ! command -v npm >/dev/null; then
  echo "npm is required but not installed. Please install Node.js first."
  exit 1
fi

# Create project directory
mkdir -p "$PWD/vue-project"
cd "$PWD/vue-project"

if [ -d .git ]; then
  echo "Existing repository detected. Pulling latest changes..."
  git pull
  npm install
else
  read -p "Clone an existing repo into ~/vue-project? [y/N]: " CLONE_CHOICE
  if [[ $CLONE_CHOICE =~ ^[Yy]$ ]]; then
    DEFAULT_REPO="git@github.com:kwidoo/admin-ui.git"
    read -p "Repository to clone (press Enter for $DEFAULT_REPO): " REPO_URL
    REPO_URL=${REPO_URL:-$DEFAULT_REPO}
    git clone "$REPO_URL" .
    npm install
  else
    read -p "Skip project setup and continue? [y/N]: " SKIP_CHOICE
    if [[ $SKIP_CHOICE =~ ^[Yy]$ ]]; then
      echo "Skipping project setup. You can set up your project manually later."
    else
      npm create vue@latest . -- --typescript --jsx --router --pinia --eslint --vitest --playwright
      npm install tailwindcss postcss autoprefixer @headlessui/vue @heroicons/vue
      npx tailwindcss init -p
    fi
  fi
fi

# Create RAG indexing script
mkdir -p scripts
cp "$REPO_ROOT/src/rag_indexer.py" scripts/
cp "$REPO_ROOT/src/docs_indexer.py" scripts/

# Create launch script
# Launch script
cat > "$PWD/launch-env.sh" <<'EOL'
#!/bin/bash
source "$PWD/.venv/bin/activate"
ollama serve > /dev/null 2>&1 &
python -m http.server 8000 --directory "$PWD/vue-project" > /dev/null 2>&1 &
python "$HOME/vue-project/scripts/rag_indexer.py"
echo "AI environment ready! Open VSCode and configure Continue.dev"
EOL

chmod +x "$PWD/launch-env.sh"

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

source "$PWD/.venv/bin/activate"

python -m scripts.agents.agent_controller "$@"
EOL

chmod +x run_agent.sh

# VSCode extensions
if command -v code >/dev/null; then
  code --install-extension Continue.continue
  code --install-extension Vue.volar
  code --install-extension bradlc.vscode-tailwindcss
else
  echo "VSCode 'code' command not found; skipping extension installation."
fi

echo "Setup complete!"
echo "Run ~/launch-env.sh to start the AI environment"
echo "CD to ~/vue-project and run npm run dev to start Vue development server"
