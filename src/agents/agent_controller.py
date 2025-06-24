import importlib

try:
    Continue = importlib.import_module("continue.api").Continue
    CodebaseContext = importlib.import_module("continue.plugins").CodebaseContext
except ModuleNotFoundError:
    class Continue:
        async def complete(self, *args, **kwargs):
            raise RuntimeError("Continue package is not installed")

    class CodebaseContext:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Continue package is not installed")
from verification.orchestrator import VerificationPipeline
from .prompt_templates import (
    NEW_COMPONENT_TEMPLATE,
    PINIA_STORE_TEMPLATE,
    API_SERVICE_TEMPLATE,
    ROUTER_CONFIG_TEMPLATE,
    DEBUG_TEMPLATE,
)
import subprocess
import os
import requests
import json
import asyncio

class AgentController:
    def __init__(self):
        """Initialize agent controller with Continue API"""
        self.c = Continue()
        self.code_context = CodebaseContext(n_retrieve=10)
        self.verifier = VerificationPipeline()
        self.git_agents = {}  # repo_url: GitAgent

    async def refactor_component(self, component_path):
        """Refactor Vue component to Composition API"""
        print(f"Refactoring component: {component_path}")
        await self.c.edit(
            filepath=component_path,
            prompt="Refactor this component to use Vue 3 Composition API with TypeScript",
            context=[self.code_context]
        )
        await self.run_tests()
        print(f"Successfully refactored {component_path}")

    async def generate_component(self, component_name, props):
        """Generate new Vue component"""
        component_path = f"src/components/{component_name}.vue"
        os.makedirs(os.path.dirname(component_path), exist_ok=True)

        props_str = ", ".join(props) if isinstance(props, list) else props

        prompt = f"""
        Create Vue3 component with:
        - Composition API
        - TypeScript
        - Tailwind styling
        - Props: {props_str}
        - Emit events for user interactions
        - Ensure <script> comes before <template>
        - Avoid <style> unless absolutely necessary
        - Place all type definitions in ./types folder
        """

        await self.c.edit(
            filepath=component_path,
            prompt=prompt,
            context=[self.code_context]
        )

        print(f"Generated component: {component_path}")
        return component_path

    async def generate_vue_component(self, name, props=None, emits=None, slots=None, description=""):
        """Generate Vue component using research prompts"""
        component_path = f"src/components/{name}.vue"
        os.makedirs(os.path.dirname(component_path), exist_ok=True)

        prompt = NEW_COMPONENT_TEMPLATE.format(
            name=name,
            props=props or {},
            emits=emits or [],
            slots=slots or [],
            description=description,
        )

        await self.c.edit(
            filepath=component_path,
            prompt=prompt,
            context=[self.code_context],
        )

        print(f"Generated component: {component_path}")
        return component_path

    async def generate_pinia_store(self, name, state_definition, getters=None, actions=None, store_type="options"):
        """Generate Pinia store following project rules"""
        store_path = f"src/stores/{name}.ts"
        os.makedirs(os.path.dirname(store_path), exist_ok=True)

        prompt = PINIA_STORE_TEMPLATE.format(
            name=name,
            store_type=store_type,
            state=state_definition,
            getters=getters or {},
            actions=actions or {},
        )

        await self.c.edit(
            filepath=store_path,
            prompt=prompt,
            context=[self.code_context],
        )

        print(f"Generated Pinia store: {store_path}")
        return store_path

    async def generate_api_service(self, service_name, endpoints):
        """Create Axios service file"""
        service_path = f"src/services/{service_name}.ts"
        os.makedirs(os.path.dirname(service_path), exist_ok=True)

        prompt = API_SERVICE_TEMPLATE.format(name=service_name, endpoints=endpoints)

        await self.c.edit(
            filepath=service_path,
            prompt=prompt,
            context=[self.code_context],
        )

        print(f"Generated API service: {service_path}")
        return service_path

    async def configure_vue_router(self, routes):
        """Update Vue Router configuration"""
        router_path = "src/router/index.ts"
        prompt = ROUTER_CONFIG_TEMPLATE.format(routes=routes)

        await self.c.edit(
            filepath=router_path,
            prompt=prompt,
            context=[self.code_context],
        )

        print("Updated router configuration")
        return router_path

    async def debug_code(self, code_snippet, error_message="", context=""):
        """Use LLM to debug code snippet"""
        prompt = DEBUG_TEMPLATE.format(code=code_snippet, error=error_message, context=context)
        return await self.c.complete(prompt, max_tokens=800)

    async def fix_api_issue(self, service_file_content, problem_description):
        """Diagnose and fix API service issues"""
        prompt = f"""{problem_description}\n\n{service_file_content}\nProvide a corrected version."""
        return await self.c.complete(prompt, max_tokens=1200)

    async def lint_and_fix(self, file_content):
        """Fix ESLint issues in provided code"""
        prompt = f"Lint and fix the following code according to project ESLint rules:\n{file_content}"
        return await self.c.complete(prompt, max_tokens=800)

    async def refactor_code(self, code_snippet, refactor_goal=""):
        """Refactor code for readability and maintain strict typing"""
        prompt = f"Refactor the following code to {refactor_goal} while keeping strict TypeScript:\n{code_snippet}"
        return await self.c.complete(prompt, max_tokens=1200)

    async def enforce_strict_typescript(self, code_snippet):
        """Convert JavaScript code to strict TypeScript"""
        prompt = f"Convert this code to strict TypeScript without using 'any':\n{code_snippet}"
        return await self.c.complete(prompt, max_tokens=1200)

    async def add_inline_comments(self, code_snippet):
        """Add inline comments to code"""
        prompt = f"Add concise inline comments to the following code:\n{code_snippet}"
        return await self.c.complete(prompt, max_tokens=600)

    async def generate_tsdoc(self, code_snippet, element_type):
        """Generate TSDoc comments"""
        prompt = f"Generate TSDoc comments for this {element_type}:\n{code_snippet}"
        return await self.c.complete(prompt, max_tokens=800)

    async def generate_readme_section(self, section_name, project_context):
        """Generate README section"""
        prompt = f"Write the {section_name} section of the README using this context:\n{project_context}"
        return await self.c.complete(prompt, max_tokens=1000)

    async def explain_task_implementation(self, high_level_task, current_codebase_context):
        """Explain how to implement a high-level task"""
        prompt = f"Explain how to implement the following task in code:\n{high_level_task}\nContext:\n{current_codebase_context}"
        return await self.c.complete(prompt, max_tokens=1000)

    async def generate_task_code_snippet(self, feature_description, component_context=""):
        """Generate code snippet for a task"""
        prompt = f"Generate code to implement this feature:\n{feature_description}\nContext:\n{component_context}"
        return await self.c.complete(prompt, max_tokens=1000)

    async def summarize_code_for_task(self, code_snippet, purpose=""):
        """Summarize existing code for task updates"""
        prompt = f"Summarize the following code for {purpose}:\n{code_snippet}"
        return await self.c.complete(prompt, max_tokens=800)

    async def run_tests(self):
        """Run project tests"""
        print("Running tests...")
        await self.run_command("npm run test:unit")

    async def run_command(self, command):
        """Execute shell command"""
        print(f"Running command: {command}")
        process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Command failed: {stderr.decode()}")
            raise Exception(f"Command failed: {stderr.decode()}")
        return stdout.decode()

    async def setup_new_feature(self, feature_name):
        """End-to-end feature setup"""
        print(f"Setting up new feature: {feature_name}")
        await self.run_command(f"git checkout -b feature/{feature_name}")

        # Generate view component
        await self.generate_component(f"{feature_name}View", ["user", "settings"])

        # Update router
        await self.c.edit(
            filepath="src/router/index.ts",
            prompt=f"Add route for /{feature_name.lower()} pointing to {feature_name}View",
            context=[self.code_context]
        )

        # Run tests
        await self.run_tests()

        # Commit changes
        await self.c.commit(f"Implement {feature_name} feature")

        # Push changes
        await self.run_command("git push -u origin HEAD")

        print(f"Feature {feature_name} setup complete!")

    async def ci_cd_pipeline(self):
        """Run CI/CD pipeline"""
        print("Running CI/CD pipeline...")
        await self.run_command("npm install")
        await self.run_tests()
        await self.run_command("npm run build")
        await self.run_command("aws s3 sync dist/ s3://my-app-bucket")
        await self.c.commit("Production deployment", push=True)
        print("CI/CD pipeline completed successfully!")

    async def generate_verified_component(self, requirements):
        """Generate and verify component"""
        # Step 1: Generate initial version
        component_code = await self.generate_component(
            requirements["name"],
            requirements["props"],
            requirements.get("styles")
        )

        # Step 2: Run verification pipeline
        context = self.knowledge.query_codebase(
            f"Vue components similar to {requirements['name']}"
        )

        result = self.verifier.iterative_correction(
            component_code,
            requirements,
            context
        )

        if result["verified"]:
            return result["code"]
        else:
            # Fallback to human review
            return self.human_review_fallback(result)

    def human_review_fallback(self, verification_result):
        """Present for human review when verification fails"""
        print("⚠️ AI verification failed. Please review manually:")
        print(f"Verification Score: {verification_result['report']['verification_score']:.2f}")
        print("\nVerification Report:")
        print(json.dumps(verification_result["report"], indent=2))
        print("\nGenerated Code:")
        print(verification_result["code"])

        # Create task in project management
        self.create_review_task(verification_result)
        return verification_result["code"]

    def get_git_agent(self, repo_url):
        """Get or create Git agent for repository"""
        if repo_url not in self.git_agents:
            self.git_agents[repo_url] = GitAgent(repo_url)
        return self.git_agents[repo_url]

    async def execute_task(self, task_description, repo_path=None):
        """
        Execute development task with Git integration
        repo_path: Local path or Git URL
        """
        if repo_path and isinstance(repo_path, str) and repo_path.startswith("http"):
            # Handle Git URL
            git_agent = self.get_git_agent(repo_path)
            return git_agent.ai_development_workflow(task_description)

        # Existing local development workflow
        # ...existing implementation...

    async def repository_task(self, repo_url, task_description):
        """Public method for repository tasks"""
        git_agent = self.get_git_agent(repo_url)
        return git_agent.ai_development_workflow(task_description)

class DesignToComponentAgent:
    def __init__(self):
        """Initialize design-to-component agent"""
        self.c = Continue()
        self.agent_controller = AgentController()

    async def generate_from_figma(self, figma_url):
        """Convert Figma design to Vue component"""
        print(f"Generating component from Figma design: {figma_url}")

        # In a real implementation, this would use the Figma API
        # For this example, we'll simulate the API response
        design_data = {
            "name": "ProductCard",
            "props": ["product", "onAddToCart"]
        }

        css_specs = self.extract_css(design_data)

        # Generate component structure
        component_path = await self.agent_controller.generate_component(
            component_name=design_data["name"],
            props=design_data["props"]
        )

        # Apply Tailwind classes
        await self.c.edit(
            filepath=f"src/components/{design_data['name']}.vue",
            prompt=f"Apply these Tailwind classes: {css_specs}"
        )

        print(f"Generated component from design: {component_path}")
        return component_path

    def extract_css(self, design_data):
        """Convert design specs to Tailwind classes"""
        # Implementation would vary based on design system
        return "bg-gray-100 p-4 rounded-lg shadow-md flex flex-col space-y-2"

if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) < 2:
            print("Usage: python agent_controller.py [command] [args]")
            sys.exit(1)

        command = sys.argv[1]
        agent = AgentController()
        design_agent = DesignToComponentAgent()

        if command == "refactor_component":
            if len(sys.argv) < 3:
                print("Usage: python agent_controller.py refactor_component [component_path]")
                sys.exit(1)
            await agent.refactor_component(sys.argv[2])

        elif command == "generate_component":
            if len(sys.argv) < 4:
                print("Usage: python agent_controller.py generate_component [name] [props]")
                sys.exit(1)
            await agent.generate_component(sys.argv[2], json.loads(sys.argv[3]))

        elif command == "generate_vue_component":
            if len(sys.argv) < 3:
                print("Usage: python agent_controller.py generate_vue_component [name]")
                sys.exit(1)
            name = sys.argv[2]
            props = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
            await agent.generate_vue_component(name, props)

        elif command == "generate_pinia_store":
            if len(sys.argv) < 4:
                print("Usage: python agent_controller.py generate_pinia_store [name] [state_json]")
                sys.exit(1)
            name = sys.argv[2]
            state = json.loads(sys.argv[3])
            await agent.generate_pinia_store(name, state)

        elif command == "generate_api_service":
            if len(sys.argv) < 4:
                print("Usage: python agent_controller.py generate_api_service [name] [endpoints_json]")
                sys.exit(1)
            name = sys.argv[2]
            endpoints = json.loads(sys.argv[3])
            await agent.generate_api_service(name, endpoints)

        elif command == "configure_router":
            if len(sys.argv) < 3:
                print("Usage: python agent_controller.py configure_router [routes_json]")
                sys.exit(1)
            routes = json.loads(sys.argv[2])
            await agent.configure_vue_router(routes)

        elif command == "setup_feature":
            if len(sys.argv) < 3:
                print("Usage: python agent_controller.py setup_feature [feature_name]")
                sys.exit(1)
            await agent.setup_new_feature(sys.argv[2])

        elif command == "generate_from_figma":
            if len(sys.argv) < 3:
                print("Usage: python agent_controller.py generate_from_figma [figma_url]")
                sys.exit(1)
            await design_agent.generate_from_figma(sys.argv[2])

        elif command == "ci_cd":
            await agent.ci_cd_pipeline()

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    asyncio.run(main())
