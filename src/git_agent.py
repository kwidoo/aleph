import subprocess
import os
import json
from pathlib import Path
import importlib

try:
    Continue = importlib.import_module("continue.api").Continue
except ModuleNotFoundError:
    class Continue:
        async def complete(self, *args, **kwargs):
            raise RuntimeError("Continue package is not installed")
from agents.agent_controller import AgentController
from verification.orchestrator import VerificationPipeline

class GitAgent:
    def __init__(self, repo_url, branch="main", work_dir="/projects"):
        self.repo_url = repo_url
        self.branch = branch
        self.work_dir = Path(work_dir)
        self.repo_name = self._extract_repo_name()
        self.repo_path = self.work_dir / self.repo_name
        self.c = Continue()
        self.agent = AgentController()
        self.verifier = VerificationPipeline()

        # Credential handling
        self.git_user = os.getenv("GIT_USER", "ai-dev-bot")
        self.git_email = os.getenv("GIT_EMAIL", "ai-bot@example.com")

    def _extract_repo_name(self):
        """Extract repository name from URL"""
        if self.repo_url.endswith(".git"):
            return self.repo_url.split("/")[-1][:-4]
        return self.repo_url.split("/")[-1]

    def _run_git_command(self, command):
        """Execute git command with error handling"""
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = f"Git command failed: {e.stderr.strip()}"
            self.c.log_error(error_msg)
            raise RuntimeError(error_msg)

    def clone_repository(self):
        """Clone repository if not exists, else pull updates"""
        if not self.repo_path.exists():
            self.work_dir.mkdir(parents=True, exist_ok=True)
            self._run_git_command(["clone", self.repo_url, self.repo_name])
            self.c.log_info(f"Cloned repository: {self.repo_name}")
        else:
            self._run_git_command(["pull", "origin", self.branch])
            self.c.log_info(f"Updated repository: {self.repo_name}")

        # Configure git identity
        self._run_git_command(["config", "user.name", self.git_user])
        self._run_git_command(["config", "user.email", self.git_email])

        return self.repo_path

    def create_branch(self, branch_name):
        """Create and switch to new feature branch"""
        self._run_git_command(["checkout", "-b", branch_name])
        return branch_name

    def get_changed_files(self):
        """Get list of modified files"""
        status = self._run_git_command(["status", "--porcelain"])
        return [line[3:] for line in status.split("\n") if line]

    def generate_commit_message(self):
        """AI-generated commit message based on changes"""
        changed_files = self.get_changed_files()
        diff = self._run_git_command(["diff", "--staged"])

        prompt = f"""
        Write a professional Git commit message based on these changes:

        Changed files:
        {json.dumps(changed_files, indent=2)}

        Code diff:
        {diff}

        Use conventional commit format:
        <type>(<scope>): <description>

        <body>

        Example:
        feat(authentication): add OAuth2 login support

        - Implemented Google OAuth integration
        - Added token refresh mechanism
        - Updated user model with auth fields
        """
        return self.c.complete(prompt, max_tokens=200)

    def commit_changes(self, message=None):
        """Commit changes with AI-generated message"""
        # Stage all changes
        self._run_git_command(["add", "."])

        # Generate message if not provided
        if not message:
            message = self.generate_commit_message()

        # Commit
        self._run_git_command(["commit", "-m", message])
        return message

    def push_changes(self, branch=None):
        """Push changes to remote repository"""
        branch = branch or self.branch
        self._run_git_command(["push", "origin", branch])
        return f"Pushed to origin/{branch}"

    def create_pull_request(self, title, description):
        """Create pull request using GitHub CLI"""
        try:
            result = subprocess.run(
                ["gh", "pr", "create", "--title", title, "--body", description],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.c.log_warning("GitHub CLI not available. Skipping PR creation.")
            return None

    def ai_development_workflow(self, task_description):
        """End-to-end AI development workflow"""
        # Step 1: Setup repository
        self.clone_repository()

        # Step 2: Create feature branch
        branch_name = f"ai-feature/{int(time.time())}"
        self.create_branch(branch_name)

        # Step 3: Perform development task
        development_report = self.agent.execute_task(task_description, self.repo_path)

        # Step 4: Verify changes
        verification_report = self.verify_changes()

        # Step 5: Commit and push
        commit_message = self.commit_changes()
        push_result = self.push_changes(branch_name)

        # Step 6: Create PR
        pr_title = f"AI Implementation: {task_description[:50]}"
        pr_body = f"""
        ## AI-Generated Feature Implementation

        **Task Description:**
        {task_description}

        **Development Report:**
        {json.dumps(development_report, indent=2)}

        **Verification Report:**
        {verification_report}
        """
        pr_result = self.create_pull_request(pr_title, pr_body)

        return {
            "branch": branch_name,
            "commit": commit_message,
            "push": push_result,
            "pr": pr_result,
            "development": development_report,
            "verification": verification_report
        }

    def verify_changes(self):
        """Run verification on all changed files"""
        changed_files = self.get_changed_files()
        verification_results = {}

        for file in changed_files:
            file_path = self.repo_path / file
            if file_path.exists():
                with open(file_path, "r") as f:
                    content = f.read()

                # Determine file type
                if file.endswith(".vue"):
                    file_type = "vue"
                    requirements = self._get_vue_requirements(file)
                elif file.endswith(".ts"):
                    file_type = "typescript"
                    requirements = self._get_ts_requirements(file)
                else:
                    continue

                # Verify file
                result = self.verifier.verify(
                    content,
                    requirements,
                    context=self.agent.knowledge.query_codebase(file)
                )
                verification_results[file] = result

                # Correct if needed
                if not result["verified"]:
                    corrected = self.verifier.generate_corrections(result)
                    with open(file_path, "w") as f:
                        f.write(corrected)

        return verification_results

    def _get_vue_requirements(self, file_path):
        """Extract requirements from Vue file context"""
        # In a real implementation, this would parse component metadata
        return {
            "type": "vue",
            "name": Path(file_path).stem,
            "patterns": ["<template>", "<script setup>", "defineProps"],
            "rules": ["composition-api", "typescript", "tailwind"]
        }

    def _get_ts_requirements(self, file_path):
        """Extract requirements from TypeScript file"""
        return {
            "type": "typescript",
            "patterns": ["interface", "function", "export"],
            "rules": ["strict-types", "eslint"]
        }

class GitCredentialManager:
    """Secure credential handling for Git operations"""
    def __init__(self):
        self.credential_store = os.getenv("GIT_CREDENTIAL_STORE", "memory")

    def configure_credentials(self, repo_url):
        """Configure credentials for repository access"""
        if "github.com" in repo_url:
            token = os.getenv("GITHUB_TOKEN")
            if token:
                self._configure_github_token(token)
            else:
                self.c.log_warning("GitHub token not found. Using SSH fallback")

    def _configure_github_token(self, token):
        """Set up GitHub token authentication"""
        # Configure credential helper
        subprocess.run(["git", "config", "--global", "credential.helper", "store"])

        # Add token to credential store
        credentials = f"https://{token}:x-oauth-basic@github.com"
        with open(os.path.expanduser("~/.git-credentials"), "a") as f:
            f.write(f"{credentials}\n")

        # Set GitHub API token
        os.environ["GH_TOKEN"] = token
        self.c.log_info("GitHub token configured")
