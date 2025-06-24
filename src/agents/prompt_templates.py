# Prompt templates for AgentController methods
# These are simplified prompts derived from `.github/prompt-research.md`
# and `.github/extra-prompts.md`.
# They guide the Continue API to generate Vue 3 code following project rules.

NEW_COMPONENT_TEMPLATE = """
Create a Vue 3 component named `{name}` using <script setup lang='ts'>.
Props: {props}
Emits: {emits}
Slots: {slots}
{description}
Follow project rules: <script> before <template>, use Tailwind CSS, place types in ./types and avoid <style> blocks.
"""

PINIA_STORE_TEMPLATE = """
Generate a Pinia store named `{name}` with {store_type} syntax.
State definition: {state}
Getters: {getters}
Actions: {actions}
Use strict TypeScript and output to src/stores.
"""

API_SERVICE_TEMPLATE = """
Create an Axios service `{name}` handling these endpoints:
{endpoints}
Use humps for camelCase conversion and TypeScript interfaces for requests and responses.
"""

ROUTER_CONFIG_TEMPLATE = """
Update Vue Router configuration with the following routes:
{routes}
Use createWebHistory and strict TypeScript definitions.
"""

DEBUG_TEMPLATE = """
Given this code:
{code}
And error:
{error}
{context}
Suggest a clear fix.
"""

