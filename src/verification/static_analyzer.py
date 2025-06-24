import ast
import astunparse
import subprocess
import importlib
from security_agent import SecurityAgent

try:
    Continue = importlib.import_module("continue.api").Continue
except ModuleNotFoundError:
    class Continue:
        async def complete(self, *args, **kwargs):
            raise RuntimeError("Continue package is not installed")

class StaticVerifier:
    def __init__(self):
        self.c = Continue()
        self.security = SecurityAgent()

    def verify_syntax(self, code, language="vue"):
        """Check for syntax errors"""
        try:
            if language == "vue":
                # Extract script content
                script_start = code.find("<script>") + 8
                script_end = code.find("</script>")
                script_content = code[script_start:script_end]
                ast.parse(script_content)
            elif language == "python":
                ast.parse(code)
            return True
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Syntax error: {str(e)}",
                "line": e.lineno
            }

    def verify_patterns(self, code, patterns):
        """Check for required patterns"""
        missing = []
        for pattern in patterns:
            if pattern not in code:
                missing.append(pattern)
        return missing

    def verify_security(self, code):
        """Check for security anti-patterns"""
        return self.security.scan_code_snippet(code)

    def lint_code(self, code, language="vue"):
        """Run language-specific linter"""
        temp_file = f"temp_verify.{language}"
        with open(temp_file, "w") as f:
            f.write(code)

        if language == "vue":
            result = subprocess.run(
                ["eslint", temp_file],
                capture_output=True,
                text=True
            )
        elif language == "python":
            result = subprocess.run(
                ["pylint", temp_file],
                capture_output=True,
                text=True
            )

        return result.stdout if result.returncode != 0 else None

    def full_static_check(self, code, requirements):
        """Comprehensive static verification"""
        report = {
            "syntax": self.verify_syntax(code, requirements.get("language", "vue")),
            "patterns": self.verify_patterns(code, requirements.get("patterns", [])),
            "security": self.verify_security(code),
            "linting": self.lint_code(code, requirements.get("language", "vue"))
        }

        report["valid"] = (
            report["syntax"] is True and
            not report["patterns"] and
            report["security"]["issues"] == 0 and
            report["linting"] is None
        )

        return report
