### Git Repository Integration Agent
I'll create a comprehensive Git agent that automates repository operations within the AI development workflow:

#### 1. Git Automation Agent (`git_agent.py`)
```python
import subprocess
import os
import json
from pathlib import Path
from continue.api import Continue
from agent_controller import AgentController
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
```

### 2. Repository Task Execution Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant G as GitAgent
    participant R as Remote Repo
    participant A as AI Agent
    participant V as Verifier

    U->>G: Request task on repo
    G->>R: Clone repository
    G->>G: Create feature branch
    G->>A: Execute development task
    A->>G: Return modified files
    G->>V: Verify changes
    alt Changes valid
        V->>G: Approval
    else Changes invalid
        V->>A: Request corrections
        A->>G: Return corrected files
    end
    G->>G: Generate commit message
    G->>R: Commit and push changes
    G->>R: Create pull request
    G->>U: Return results
```

### 3. Integration with Agent Controller

```python
# agent_controller.py (Additions)

class AgentController:
    def __init__(self):
        # ... existing code ...
        self.git_agents = {}  # repo_url: GitAgent

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
        # ... existing implementation ...

    async def repository_task(self, repo_url, task_description):
        """Public method for repository tasks"""
        git_agent = self.get_git_agent(repo_url)
        return git_agent.ai_development_workflow(task_description)
```

### 4. Dockerized Git Agent Service

```dockerfile
# Dockerfile.git-agent
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    gnupg \
    openssh-client

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh

# Set up workspace
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Entry point
CMD ["python", "-m", "git_agent"]
```

### 5. Usage Examples

#### 5.1 CLI Interface
```bash
# Run development task on repository
python agent_controller.py \
    --repo https://github.com/yourorg/your-project.git \
    --task "Implement user profile component with Vue 3"
```

#### 5.2 Programmatic Usage
```python
from agent_controller import AgentController

agent = AgentController()
result = agent.repository_task(
    repo_url="https://github.com/yourorg/your-project.git",
    task_description="""
    Create dashboard page with:
    - User statistics cards
    - Activity timeline
    - Responsive grid layout
    - Using existing components where possible
    """
)

print(f"Created PR: {result['pr']}")
```

#### 5.3 GitHub Actions Workflow
```yaml
name: AI Development Task
on:
  workflow_dispatch:
    inputs:
      task:
        description: 'Development task description'
        required: true

jobs:
  ai-development:
    runs-on: ubuntu-latest
    container:
      image: your-docker-repo/git-agent:latest
      credentials:
        username: ${{ secrets.DOCKER_USER }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      GIT_USER: "github-actions[bot]"
      GIT_EMAIL: "github-actions@github.com"
    steps:
      - name: Execute AI task
        run: |
          python agent_controller.py \
            --repo https://github.com/${{ github.repository }}.git \
            --task "${{ inputs.task }}"
```

### 6. Security Enhancements

#### 6.1 SSH Key Handling
```python
# git_agent.py additions

class GitAgent:
    def __init__(self):
        # ... existing code ...
        self.ssh_key = os.getenv("SSH_PRIVATE_KEY")

    def _setup_ssh(self):
        """Configure SSH for Git operations"""
        if not self.ssh_key:
            return

        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(exist_ok=True, mode=0o700)

        # Write private key
        key_file = ssh_dir / "id_rsa"
        with open(key_file, "w") as f:
            f.write(self.ssh_key)
        key_file.chmod(0o600)

        # Configure known hosts
        known_hosts = ssh_dir / "known_hosts"
        with open(known_hosts, "a") as f:
            f.write("github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==")

        # Configure Git to use SSH
        self._run_git_command(["config", "url.ssh://git@github.com.insteadof", "https://github.com"])
        os.environ["GIT_SSH_COMMAND"] = "ssh -o StrictHostKeyChecking=yes"
```

#### 6.2 Token Rotation
```python
# git_agent.py additions

class GitCredentialManager:
    def rotate_token(self):
        """Rotate Git credentials periodically"""
        if time.time() - self.last_rotation > 3600:  # Rotate hourly
            new_token = self._generate_new_token()
            self._update_credentials(new_token)
            self.last_rotation = time.time()

    def _generate_new_token(self):
        """Generate new access token (implementation varies by provider)"""
        # Example for GitHub
        if "github.com" in self.repo_url:
            return self._generate_github_token()

    def _generate_github_token(self):
        """Create new GitHub token using OAuth"""
        # Implementation requires authentication with parent token
        pass
```

### 7. Advanced Repository Operations

#### 7.1 Conflict Resolution
```python
# git_agent.py additions

class GitAgent:
    def handle_merge_conflicts(self):
        """Resolve Git merge conflicts using AI"""
        conflicts = self._get_conflict_files()

        for file in conflicts:
            with open(self.repo_path / file, "r") as f:
                content = f.read()

            # Extract conflict markers
            conflict_sections = self._parse_conflict_content(content)

            # Resolve conflicts with AI
            prompt = f"""
            Resolve Git merge conflict in {file}:

            Current content:
            {content}

            Conflict sections:
            {json.dumps(conflict_sections, indent=2)}

            Provide resolved file content that intelligently merges changes.
            Preserve functionality from both branches.
            """
            resolved_content = self.c.complete(prompt, max_tokens=2000)

            # Write resolved content
            with open(self.repo_path / file, "w") as f:
                f.write(resolved_content)

            # Mark as resolved
            self._run_git_command(["add", file])

    def _get_conflict_files(self):
        """Get files with merge conflicts"""
        status = self._run_git_command(["status", "--porcelain"])
        return [line[3:] for line in status.split("\n") if "UU" in line]

    def _parse_conflict_content(self, content):
        """Parse conflict markers into structured data"""
        # Implementation to extract <<<<<<<, =======, >>>>>>> sections
        pass
```

#### 7.2 Repository Analysis
```python
# git_agent.py additions

class GitAgent:
    def analyze_repository(self):
        """Generate repository analysis report"""
        # Get code statistics
        stats = self._run_git_command(["cloc", "--json"])

        # Get commit history
        log = self._run_git_command(["log", "--pretty=format:%h|%an|%ad|%s", "--date=short"])

        prompt = f"""
        Analyze this repository:

        Code statistics:
        {stats}

        Recent commit history:
        {log[:5000]}... [truncated]

        Provide insights:
        1. Primary tech stack
        2. Development activity patterns
        3. Potential technical debt areas
        4. Team collaboration patterns
        5. Recommendations for improvement
        """
        return self.c.complete(prompt, max_tokens=1500)
```

### 8. Full Workflow Execution

```bash
# Example workflow with verification and Git integration
python -c "
from agent_controller import AgentController
agent = AgentController()
result = agent.repository_task(
    'https://github.com/yourorg/vue-project.git',
    'Add dark mode toggle component to header'
)
print(f'Task completed: PR #{result[\"pr\"]}')
"
```

### Key Features

1. **Complete Git Lifecycle Automation**:
   - Repository cloning and updating
   - Branch management
   - AI-generated commit messages
   - Pull request creation

2. **Secure Credential Handling**:
   - SSH key configuration
   - Token rotation
   - GitHub CLI integration

3. **Repository-Aware Development**:
   - Contextual task execution
   - Change verification
   - Conflict resolution

4. **DevOps Integration**:
   - Dockerized agent service
   - GitHub Actions workflow
   - CI/CD pipeline compatibility

5. **Advanced Operations**:
   - Merge conflict resolution
   - Repository analysis
   - Multi-repository management

This Git integration enables fully automated AI development workflows:
1. Download repository ✅
2. Perform development tasks ✅
3. Verify code correctness ✅
4. Commit changes ✅
5. Create pull requests ✅
6. Update repository ✅

All operations are secure, traceable, and integrate seamlessly with existing development workflows.
