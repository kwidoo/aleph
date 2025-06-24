# App Structure and Functionality Overview

## Agent: TestAgent
- **Purpose**: Generates, runs, and fixes unit tests for Vue components.
- **Key Methods**:
  - `async def generate_test(self, component_path: str)`: Generates Vitest unit tests using AI.
  - `async def run_tests(self, test_path: str = None)`: Runs tests with coverage.
  - `async def fix_failing_tests(self, test_path: str)`: Uses AI to fix failing tests.
  - `async def generate_story(self, component_path: str)`: Generates Storybook stories.
- **Used in**: `AgentController.run_tests()`
- **Notes**: Uses subprocess for test execution, integrates with Continue API for AI code generation.

## Agent: AccessibilityAgent
- **Purpose**: Audits Vue components for accessibility (WCAG) compliance.
- **Key Method**: `async def audit_component(self, component_name, props=None, standard="wcag21aa")`
- **Used in**: Accessibility audit workflows.
- **Notes**: Uses Playwright for browser automation, generates HTML harness, runs axe-core, outputs JSON reports.

## Agent: PerformanceAgent
- **Purpose**: Benchmarks and analyzes Vue component performance.
- **Key Method**: `async def benchmark_component(self, component_name, props=None, iterations=50)`
- **Used in**: Performance audit workflows.
- **Notes**: Uses Playwright for browser automation, collects mount/update/memory metrics, outputs JSON and plots.

## Agent: VisualRegressionAgent
- **Purpose**: Performs visual regression testing on Vue components.
- **Key Methods**:
  - `async def capture_component_screenshot(self, component_name, props=None, viewport=(1280, 720))`
  - `async def compare_with_baseline(self, component_name, threshold=0.01)`
- **Used in**: Visual regression workflows.
- **Notes**: Uses Playwright and OpenCV for screenshot capture and image diffing.

## Agent: FigmaToVueAgent / FigmaParser
- **Purpose**: Converts Figma designs to Vue component specs and code.
- **Key Methods**:
  - `async def generate_component(self, figma_url: str)`
  - `def convert_to_component_spec(self, figma_data: Dict)`
- **Used in**: Design-to-component workflows.
- **Notes**: Uses Figma API, extracts props/styles/layout, applies Tailwind classes.

## Agent: DesignToComponentAgent
- **Purpose**: Orchestrates Figma-to-Vue component generation.
- **Key Method**: `async def generate_from_figma(self, figma_url)`
- **Used in**: CLI and controller workflows.

---

## Controller: AgentController
- **Purpose**: Orchestrates agent workflows and CLI commands.
- **Key Methods**:
  - `async def refactor_component(self, component_path)`
  - `async def generate_component(self, component_name, props)`
  - `async def run_tests(self)`
  - `async def setup_new_feature(self, feature_name)`
  - `async def ci_cd_pipeline(self)`
  - `async def generate_verified_component(self, requirements)`
  - `async def execute_task(self, task_description, repo_path=None)`
- **Workflow Trigger**: Via CLI (`python agent_controller.py [command] [args]`) or as a Python module.
- **Notes**: Integrates with Continue API, VerificationPipeline, and GitAgent.

---

## Supported Workflows

### Component Generation from Figma
- **Steps**: Parse Figma → Extract spec → Generate Vue component → Apply Tailwind styles.
- **Command**: `python src/agents/figma_integration.py <figma_token> <figma_url>`

### Test Execution and Coverage
- **Steps**: Generate tests → Run tests → Analyze/fix failures → Monitor coverage.
- **Command**: `python src/agents/test_agent.py generate src/components/Component.vue`

### Accessibility and Performance Audits
- **Accessibility**: `python src/agents/accessibility_agent.py audit ComponentName`
- **Performance**: `python src/agents/performance_agent.py benchmark ComponentName`

### Visual Regression
- **Steps**: Capture screenshot → Compare with baseline → Highlight differences.
- **Command**: `python src/agents/visual_test_agent.py compare ComponentName`

### CI/CD Automation
- **Steps**: Install deps → Run tests → Build → Deploy → Commit/push.
- **Command**: `python agent_controller.py ci_cd`

---

## Example CLI Commands

```bash
# Generate a component
python agent_controller.py generate_component ProductCard '["product", "onAddToCart"]'

# Refactor a component
python agent_controller.py refactor_component src/components/LegacyComponent.vue

# Generate from Figma
python agent_controller.py generate_from_figma https://figma.com/file/12345

# Run accessibility audit
python src/agents/accessibility_agent.py audit UserCard

# Run performance benchmark
python src/agents/performance_agent.py benchmark UserCard
```

---

## How to Extend

**Checklist:**
1. Create a new agent class in `src/agents/`
2. Implement async methods for your workflow.
3. Register the agent in `AgentController` (if orchestration is needed).
4. Optionally, expose the agent via CLI by adding a command in `agent_controller.py`.

---

*All descriptions are short, declarative, and dev-friendly. Assumes familiarity with Python, async/await, and Vue3 projects.*
