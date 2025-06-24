import ast
import subprocess
import importlib

try:
    Continue = importlib.import_module("continue.api").Continue
except ModuleNotFoundError:
    class Continue:
        async def complete(self, *args, **kwargs):
            raise RuntimeError("Continue package is not installed")

class SecurityAgent:
    COMPLIANCE_STANDARDS = {
        "GDPR": ["user_data", "consent_management"],
        "HIPAA": ["medical_data", "access_controls"],
        "PCI_DSS": ["payment_processing", "encryption"]
    }

    def __init__(self):
        self.c = Continue()
        self.scanners = {
            "secret_detection": self.scan_for_secrets,
            "vulnerability": self.scan_vulnerabilities,
            "compliance": self.check_compliance
        }

    async def scan_project(self, scan_types=["all"]):
        results = {}
        if "all" in scan_types:
            scan_types = list(self.scanners.keys())

        for scan_type in scan_types:
            results[scan_type] = await self.scanners[scan_type]()

        return results

    async def scan_for_secrets(self):
        secrets = []
        for file in self._code_files():
            if any(ext in file for ext in [".env", ".config", ".json"]):
                with open(file, "r") as f:
                    content = f.read()
                    if "api_key" in content or "password" in content:
                        secrets.append(file)

        report = await self.c.complete(
            f"Found potential secrets in {len(secrets)} files. "
            "Suggest secure storage solutions."
        )
        return {"secrets_found": secrets, "report": report}

    async def scan_vulnerabilities(self):
        result = subprocess.run(["npm", "audit", "--json"], capture_output=True)
        vulnerabilities = json.loads(result.stdout)

        prompt = f"""
        Found {vulnerabilities['metadata']['vulnerabilities']['total']} vulnerabilities:
        {json.dumps(vulnerabilities, indent=2)}

        Create a prioritized remediation plan:
        1. Critical vulnerabilities
        2. Suggested updates
        3. Breaking change assessment
        """
        return await self.c.complete(prompt)

    async def check_compliance(self, standard="GDPR"):
        checks = self.COMPLIANCE_STANDARDS[standard]
        report = []

        for check in checks:
            prompt = f"""
            Check {standard} compliance for: {check}
            Analyze codebase for requirements:
            - Data encryption
            - Access controls
            - Audit trails
            - Consent management

            Identify gaps and suggest solutions.
            """
            report.append(await self.c.complete(prompt))

        return report

    def pre_commit_hook(self):
        scan_results = self.scan_project(["secret_detection"])
        if scan_results["secret_detection"]["secrets_found"]:
            print("SECURITY ALERT: Secrets detected in files!")
            return False
        return True

subprocess.run(["cp", "security_hook.py", ".git/hooks/pre-commit"])
