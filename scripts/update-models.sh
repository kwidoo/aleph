#!/bin/bash
# update-models.sh

# Update all Ollama models
if [ "$PLATFORM" = "mac" ]; then
    echo "Updating local Ollama models..."
    ollama list | awk '{print $1}' | xargs -I{} ollama pull {}
elif [ "$PLATFORM" = "ubuntu" ]; then
    echo "Updating Docker Ollama models..."
    for model in deepseek-coder:6.7b nomic-embed-text phind-coder:34b-v2; do
        docker compose run ollama ollama pull $model
    done
fi

# Reindex codebase
echo "Reindexing codebase..."
if [ "$PLATFORM" = "mac" ]; then
    source ~/.venv/bin/activate
    python ~/vue-project/scripts/rag_indexer.py --reindex
elif [ "$PLATFORM" = "ubuntu" ]; then
    docker compose exec rag-server python /app/src/rag_indexer.py --reindex
fi

# Clean Docker cache (Ubuntu)
if [ "$PLATFORM" = "ubuntu" ]; then
    echo "Cleaning Docker cache..."
    docker system prune -f
    docker volume prune -f
fi

echo "Update complete!"
