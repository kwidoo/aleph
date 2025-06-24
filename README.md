# AI-Assisted RAG Development Environment for Vue3/TypeScript

This repository contains the implementation of a multi-platform AI-assisted RAG (Retrieval Augmented Generation) development environment optimized for Vue3/TypeScript. It supports local development on macOS (M1/M3), remote development on Ubuntu Server with A4000 GPU, and a hybrid approach.

## Project Structure

```
├── config                 # Configuration files
├── scripts                # Installation and utility scripts
│   ├── macOS-native-setup.sh
│   ├── ubuntu-gpu-setup.sh
│   ├── hybrid-setup.sh
│   ├── verify-setup.sh
│   └── update-models.sh
├── src                    # Core source code
│   ├── agents             # AI agent implementations
│   │   ├── agent_controller.py
│   │   ├── figma_integration.py
│   │   ├── test_agent.py
│   │   ├── visual_test_agent.py
│   │   ├── performance_agent.py
│   │   └── accessibility_agent.py
│   ├── components         # Sample Vue3 components
│   │   └── UserCard.vue
│   ├── rag_indexer.py     # Codebase indexing for RAG
│   ├── rag_server.py      # RAG server implementation
│   ├── rag_auth.py        # Authenticated RAG endpoint
│   └── docs_indexer.py    # Documentation integration
```

## Features

- **Retrieval Augmented Generation (RAG)** - Index and query your codebase and documentation
- **AI Agent Integration** - Automated workflow for code generation, testing, and optimization
- **Multiple Platform Support** - Works on macOS and Ubuntu with GPU acceleration
- **Vue3/TypeScript Optimization** - Specifically tailored for Vue3 + TypeScript development
- **Documentation Integration** - Automatically index Vue and Tailwind documentation
- **Figma Integration** - Convert Figma designs to Vue components
- **Testing Automation** - Generate and run tests automatically
- **Performance Optimization** - Benchmark and optimize components
- **Accessibility Auditing** - Ensure components meet WCAG standards

## Installation

### 1. macOS (M1/M3) Setup

```bash
chmod +x scripts/macOS-native-setup.sh
./scripts/macOS-native-setup.sh
```

This setup script installs **Ollama** via Homebrew and automatically starts the server, so make sure Homebrew is available in your PATH.

### 2. Ubuntu Server (A4000) Setup

```bash
chmod +x scripts/ubuntu-gpu-setup.sh
./scripts/ubuntu-gpu-setup.sh
```

### 3. Hybrid Setup

```bash
chmod +x scripts/hybrid-setup.sh
./scripts/hybrid-setup.sh
```

## Usage

### Start the AI Environment

```bash
# On macOS
~/launch-ai-env.sh

# On Ubuntu Server
docker compose up -d
```

### Run an Agent Task

```bash
# Generate a component
./run_agent.sh generate_component ProductCard "['product', 'onAddToCart']"

# Refactor a component to use Composition API
./run_agent.sh refactor_component src/components/LegacyComponent.vue

# Generate from Figma design
./run_agent.sh generate_from_figma https://figma.com/file/12345
```

### Run Tests and Optimizations

```bash
# Generate tests for a component
python src/agents/test_agent.py generate src/components/UserCard.vue

# Run performance benchmark
python src/agents/performance_agent.py benchmark UserCard

# Run accessibility audit
python src/agents/accessibility_agent.py audit UserCard
```

## Performance Optimization

| Platform       | Model Choice                  | Context Size | GPU Layers | Notes                     |
|----------------|-------------------------------|--------------|------------|---------------------------|
| MacBook M3     | deepseek-coder:6.7b-q5_k_m    | 4096         | N/A        | Use Metal acceleration    |
| Mac Mini M1    | starcoder2:3b                 | 2048         | N/A        | Lower memory footprint    |
| A4000 Ubuntu   | deepseek-coder:6.7b           | 8192         | 35         | Enable CUDA acceleration  |

## Maintenance

Update models and reindex the codebase:

```bash
PLATFORM=mac ./scripts/update-models.sh  # For macOS
PLATFORM=ubuntu ./scripts/update-models.sh  # For Ubuntu Server
```

## License

MIT

## Vue3 Development Rules

To maintain consistency and quality in Vue3 development, follow these rules:

1. **File Structure**:
   - Always place `<script>` before `<template>` in Vue files.
   - Avoid using `<style>` tags. Use Tailwind CSS for styling unless absolutely necessary.

2. **Type Definitions**:
   - Store all type definitions in the `./types` folder.
   - Avoid duplicating types unnecessarily. Reuse existing types wherever possible.

3. **Code Quality**:
   - Use ESLint to enforce these rules. Ensure your editor is configured to highlight ESLint warnings and errors.

4. **Best Practices**:
   - Follow the Composition API and TypeScript conventions.
   - Use Tailwind classes for styling to maintain a consistent design system.
