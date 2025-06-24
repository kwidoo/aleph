````markdown
# GitHub Copilot Task: Describe Current App Functionality

## Goal

Generate structured and human-readable descriptions of the current functionality of the app based on existing files, focusing on purpose, workflows, and responsibilities.

## Scope

You should analyze and document the following aspects of the system:

---

### 1. Agent Architecture

- Parse all classes under `src/agents/`.
- For each agent (e.g., `TestAgent`, `DesignToComponentAgent`, etc.):
  - Summarize its core responsibility.
  - Document key public methods and expected input/output.
  - Note whether it uses async, subprocesses, or any external APIs (e.g., Continue API).
  - List related agents it interacts with.

---

### 2. Controller Logic

- Open `agent_controller.py`.
- Describe how `AgentController` manages agents.
- Document key orchestration logic like `full_component_qa`.
- Describe how workflows are triggered (CLI or Python).

---

### 3. Supported Workflows

- Based on CLI usage and controller methods, list supported workflows:
  - Component generation from Figma
  - Test execution and coverage
  - Accessibility and performance audits
  - Security and debug analysis
  - CI/CD automation

---

### 4. Example Commands

- Include runnable CLI and Python examples.
- Ensure arguments and expected formats are described.
- Note file paths, conventions, or dynamic imports used by the agents.

---

### 5. How to Extend

- Explain how new agents can be created and registered.
- Provide a short checklist:
  - Create agent class in `src/agents/`
  - Implement async methods
  - Register agent in `AgentController`
  - Optionally expose via CLI

---

### Output Format

Please use a structured format like:

```markdown
## Agent: TestAgent
- **Purpose**: Generates, runs, and fixes tests.
- **Key Method**: `async def run_tests(self, target: str)`
- **Used in**: `AgentController.run_all_tests()`
- **Notes**: Uses Jest via subprocess, outputs JUnit XML.

...

## Workflow: Full QA
- **Steps**:
  1. Generate component
  2. Run tests
  3. Check coverage
  4. Perform visual regression
  5. Audit accessibility
- **Command**: `python agent_controller.py full_component_qa ComponentName`
````

---

### Notes

* Keep all descriptions short, declarative, and dev-friendly.
* Assume reader is familiar with Python, async/await, and Vue3 projects.

