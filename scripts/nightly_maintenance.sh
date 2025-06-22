#!/bin/bash

# 1. Update models
ollama pull --update-all

# 2. Reindex knowledge base
python knowledge_manager.py --reindex

# 3. Run security scans
python security_agent.py --scan-full

# 4. Backup vector databases
tar -czf knowledge_db_backup_$(date +%F).tar.gz ./knowledge_db

# 5. Generate performance report
python optimization_engine.py --report > perf_$(date +%F).txt

# 6. Commit maintenance results
git add . && git commit -m "Nightly maintenance $(date +%F)"
