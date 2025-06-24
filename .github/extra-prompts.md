## Integrating Development Prompts into AI Agent Implementation

This document outlines tasks to integrate the researched GitHub Copilot/Codex Sonnet 3.7 friendly development prompts into the existing AI agent implementation. The goal is to empower the agents to assist developers more effectively across various stages of the Vue 3, Composition API, strict TypeScript, Tailwind CSS, Vue Router, Pinia, Axios, and Humps development workflow, while adhering to project-specific rules.

### Existing Agent Overview

Based on the provided files (`initial.md`, `phase2.md`, `phase3.md`, `phase4.md`, `README.md`, `STRUCTURE.md`), the core orchestration seems to be handled by `AgentController`, which can interact with other specialized agents like `TestAgent`, `AccessibilityAgent`, `PerformanceAgent`, and `VisualRegressionAgent`. A `VerificationPipeline` is also in place to ensure code quality.

The `README.md` also specifies critical Vue 3 Development Rules, including file structure (`<script>` before `<template>`, no `<style>` tags), type definitions (in `./types`), and ESLint usage. These rules must be reinforced in the agent's behavior.

### Proposed Integration Tasks

The integration will involve enhancing existing agent methods and introducing new ones to leverage the development prompts.

#### Task 1: Enhance `AgentController` for Core Code Generation

**Objective:** Enable the `AgentController` to generate new Vue 3 components, Pinia stores, Axios services, and Vue Router configurations based on detailed prompts, adhering to best practices and project rules.

* **1.1 Implement `generate_vue_component` method:**
    * **Description:** Add a method (e.g., `generate_vue_component(self, name: str, props: Dict, emits: List, slots: List = None, description: str = "")`) to `AgentController`. This method will construct a prompt using the "Generating New Vue Components" templates (e.g., "Basic Component," "Component with Reactive State," "Component with Emits," "Component with Slot") and pass it to the underlying LLM.
    * **Prompts Used:** All prompts from Section A ("Generating New Vue Components") of the research.
    * **Considerations:**
        * Automatically use `<script setup>` syntax.
        * Enforce strict TypeScript for props, emits, and internal state.
        * Prioritize Tailwind CSS for styling.
        * Ensure `<script>` comes before `<template>` as per `README.md`.
        * Output should be placed in `src/components/`.

* **1.2 Implement `generate_pinia_store` method:**
    * **Description:** Add a method (e.g., `generate_pinia_store(self, name: str, state_definition: Dict, getters: Dict = None, actions: Dict = None, store_type: str = "options")`) to `AgentController`. This method will use prompts from the "Generating New Pinia Stores" section to create new Pinia stores.
    * **Prompts Used:** All prompts from Section B ("Generating New Pinia Stores") of the research.
    * **Considerations:**
        * Strict TypeScript typing for state, getters, and actions.
        * Support both "options" and "setup" store types.
        * Output should be placed in `src/stores/`.

* **1.3 Implement `generate_api_service` method:**
    * **Description:** Add a method (e.g., `generate_api_service(self, service_name: str, endpoints: List[Dict])`) to `AgentController`. This method will construct prompts for Axios service creation, including Humps integration for camelCase/snake_case conversion.
    * **Prompts Used:** All prompts from Section C ("API Service Integrations") of the research.
    * **Considerations:**
        * Encapsulate Axios calls in dedicated service files (e.g., `src/services/`).
        * Ensure correct `humps` usage in `transformRequest` and `transformResponse`.
        * Strict TypeScript interfaces for request/response payloads (types in `./types`).
        * Include basic error handling (try-catch).

* **1.4 Implement `configure_vue_router` method:**
    * **Description:** Add a method (e.g., `configure_vue_router(self, routes: List[Dict])`) to `AgentController` to add or modify Vue Router configurations based on provided route definitions.
    * **Prompts Used:** All prompts from Section D ("Vue Router Routes") of the research.
    * **Considerations:**
        * Use `createWebHistory`.
        * Strict TypeScript for route definitions and props.
        * Handle dynamic and nested routes.
        * Update `src/router/index.ts`.

#### Task 2: Integrate Debugging & Fixing Capabilities

**Objective:** Enhance the agent's ability to diagnose and fix common code issues, especially TypeScript errors and API integration problems.

* **2.1 Implement `debug_code` method:**
    * **Description:** Add a method (e.g., `debug_code(self, code_snippet: str, error_message: str = "", context: str = "")`) to `AgentController`. This method will take a code snippet and an optional error message, then use the "Debugging & Error Resolution" prompts to suggest fixes.
    * **Prompts Used:** All prompts from Section A ("General Debugging & Error Resolution") and Section B ("TypeScript Error Resolution") of the research.
    * **Considerations:**
        * Prioritize clear, actionable fixes.
        * Suggest TypeScript-specific solutions for type errors.
        * Leverage `#selection` and `#file` chat variables if applicable with the underlying LLM.

* **2.2 Implement `fix_api_issue` method:**
    * **Description:** Add a method (e.g., `fix_api_issue(self, service_file_content: str, problem_description: str)`) to `AgentController`. This method will focus on diagnosing and fixing issues related to Axios, Humps, and API communication.
    * **Prompts Used:** All prompts from Section C ("API Integration (Axios, Humps) Debugging") of the research.
    * **Considerations:**
        * Analyze Axios instance configuration, interceptors, and data transformations.
        * Address Humps camelCase/snake_case conversion issues.

* **2.3 Implement `fix_routing_issue` method:**
    * **Description:** Add a method (e.g., `fix_routing_issue(self, router_config_content: str, component_content: str = "", problem_description: str = "")`) to `AgentController`. This method will help resolve common Vue Router misconfigurations.
    * **Prompts Used:** All prompts from Section D ("Vue Router Debugging") of the research.
    * **Considerations:**
        * Verify route definitions, dynamic params, prop passing, and nested routes.

#### Task 3: Implement Code Quality & Styling Automation

**Objective:** Enable the agent to enforce code quality standards, apply styling best practices, and refactor code.

* **3.1 Implement `lint_and_fix` method:**
    * **Description:** Add a method (e.g., `lint_and_fix(self, file_content: str)`) to `AgentController`. This method will use prompts to identify and suggest fixes for ESLint violations and general code formatting issues.
    * **Prompts Used:** All prompts from Section A ("Enforcing ESLint Rules & Code Formatting") of the research.
    * **Considerations:**
        * Refer to project's `.eslintrc.js` (or similar) and `plugin:vue/recommended`.
        * Prioritize fixes that improve readability and maintainability.

* **3.2 Implement `optimize_tailwind_css` method:**
    * **Description:** Add a method (e.g., `optimize_tailwind_css(self, vue_template_content: str)`) to `AgentController`. This method will identify redundant or inefficient Tailwind CSS class usage and suggest optimizations.
    * **Prompts Used:** All prompts from Section B ("Applying Tailwind CSS Best Practices") of the research.
    * **Considerations:**
        * Focus on utility-first principles.
        * Suggest responsive patterns.

* **3.3 Implement `refactor_code` method:**
    * **Description:** Add a method (e.g., `refactor_code(self, code_snippet: str, refactor_goal: str = "")`) to `AgentController`. This method will apply general refactoring principles, extract composables, simplify expressions, and improve naming.
    * **Prompts Used:** All prompts from Section C ("Refactoring for Readability & Maintainability") of the research.
    * **Considerations:**
        * Maintain strict TypeScript types during refactoring.
        * Ensure extracted logic is reusable.

* **3.4 Implement `enforce_strict_typescript` method:**
    * **Description:** Add a method (e.g., `enforce_strict_typescript(self, code_snippet: str)`) to `AgentController`. This method will convert JavaScript to strict TypeScript, explicitly type variables, and eliminate `any` usage.
    * **Prompts Used:** All prompts from Section D ("Ensuring Strict TypeScript Compliance") of the research.
    * **Considerations:**
        * Identify and suggest proper interfaces/types.
        * Utilize type guards where appropriate for external data.

#### Task 4: Develop Documentation Generation Features

**Objective:** Enable the agent to generate various forms of documentation, aiding in project maintainability.

* **4.1 Implement `add_inline_comments` method:**
    * **Description:** Add a method (e.g., `add_inline_comments(self, code_snippet: str)`) to `AgentController`. This method will add concise inline comments to code.
    * **Prompts Used:** All prompts from Section A ("Inline Comments") of the research.

* **4.2 Implement `generate_tsdoc` method:**
    * **Description:** Add a method (e.g., `generate_tsdoc(self, code_snippet: str, element_type: str)`) to `AgentController` to generate TSDoc comments for components, stores, functions, and interfaces.
    * **Prompts Used:** All prompts from Section B ("JSDoc/TSDoc for Functions, Components, and Stores") of the research.
    * **Considerations:**
        * Automate based on context (e.g., if it's a Vue component, include props/emits).

* **4.3 Implement `generate_readme_section` method:**
    * **Description:** Add a method (e.g., `generate_readme_section(self, section_name: str, project_context: Dict)`) to `AgentController`. This method will generate specific sections for the `README.md` file (e.g., Getting Started, Project Structure, Contributing, API Endpoints).
    * **Prompts Used:** All prompts from Section C ("README File Sections") of the research.
    * **Considerations:**
        * `project_context` should include information about dependencies, existing folder structure, and API routes.

#### Task 5: Create Task Update Automation

**Objective:** Allow the agent to automatically generate detailed code explanations or implementation plans for task management systems.

* **5.1 Implement `explain_task_implementation` method:**
    * **Description:** Add a method (e.g., `explain_task_implementation(self, high_level_task: str, current_codebase_context: str)`) to `AgentController`. This method will translate high-level tasks into detailed code implementation steps or high-level overviews.
    * **Prompts Used:** All prompts from Section A ("Translating High-Level Tasks to Code Implementation Details") of the research.

* **5.2 Implement `generate_task_code_snippet` method:**
    * **Description:** Add a method (e.g., `generate_task_code_snippet(self, feature_description: str, component_context: str = "")`) to `AgentController`. This method will generate ready-to-paste code snippets for task updates.
    * **Prompts Used:** All prompts from Section B ("Generating Code Snippets for Task Updates") of the research.

* **5.3 Implement `summarize_code_for_task` method:**
    * **Description:** Add a method (e.g., `summarize_code_for_task(self, code_snippet: str, purpose: str = "")`) to `AgentController`. This method will explain existing code, its purpose, and functionality for task updates, targeting different audiences (e.g., new team members, design review).
    * **Prompts Used:** All prompts from Section C ("Explaining Existing Code for Task Updates") of the research.

### Cross-Cutting Integration Considerations

* **Prompt Management:** Store the detailed prompts (or prompt templates) as internal constants or configuration files within the agent.
* **Contextualization:** Ensure that agent methods dynamically inject relevant code context (`#selection`, `#file`, `@workspace` equivalents) into the prompts sent to the LLM.
* **Verification Pipeline Integration:** For any code generated or modified by these agent tasks, automatically route the output through the existing `VerificationPipeline` (as described in `phase3.md`) to ensure correctness, adherence to standards, and avoid hallucinations. The `AgentController`'s `generate_verified_component` method is an example of this.
* **Adherence to Vue3 Development Rules:** Implement internal checks or pre-prompt instructions within the agent to strictly follow the "Vue3 Development Rules" from `README.md` (e.g., `script` before `template`, use Tailwind, types in `./types`, ESLint compliance).
* **CLI Exposure:** For key functionalities, expose them via the `AgentController`'s CLI interface (similar to examples in `STRUCTURE.md`) for easy developer access.

By implementing these tasks, the AI agent will become a highly effective and context-aware development assistant for Vue 3 projects, significantly boosting productivity and code quality.