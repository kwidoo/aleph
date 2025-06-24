import importlib

try:
    Continue = importlib.import_module("continue.api").Continue
except ModuleNotFoundError:
    class Continue:
        async def complete(self, *args, **kwargs):
            raise RuntimeError("Continue package is not installed")

class PeerReviewer:
    REVIEW_SYSTEM_PROMPT = """
    You are a senior code reviewer specialized in Vue and TypeScript.
    Your task is to verify AI-generated code for:
    - Correct implementation of requirements
    - Absence of hallucinations or outdated patterns
    - Adherence to best practices

    Provide detailed feedback and corrections when needed.
    """

    def __init__(self):
        self.c = Continue()
        self.review_model = "deepseek-coder:6.7b"  # Conservative model

    def review_code(self, generated_code, requirements, context):
        """Conduct AI peer review"""
        with self.c.switch_model(self.review_model):
            return self.c.complete(
                prompt=f"""
                [REVIEW TASK]
                Verify this AI-generated code against requirements:

                Requirements:
                {requirements}

                Context:
                {context}

                Generated Code:
                {generated_code}

                [REVIEW GUIDELINES]
                1. Check for hallucinations (incorrect APIs, imaginary methods)
                2. Verify requirement implementation
                3. Identify outdated patterns
                4. Suggest improvements
                5. Provide corrected code if needed

                Return JSON:
                {{
                    "verified": bool,
                    "issues": [str],
                    "corrections": str,
                    "confidence": 0-1
                }}
                """,
                system_prompt=self.REVIEW_SYSTEM_PROMPT,
                format="json"
            )

    def cross_model_verification(self, generated_code, requirements):
        """Verify with multiple models"""
        models = ["deepseek-coder:6.7b", "llama3.1:8b", "phind-coder:34b"]
        results = []

        for model in models:
            with self.c.switch_model(model):
                result = self.c.complete(
                    f"Does this code correctly implement: {requirements}?\nCode: {generated_code}\nAnswer:",
                    max_tokens=1
                )
                results.append("yes" in result.lower())

        # Consensus-based verification
        confidence = sum(results) / len(results)
        return {
            "verified": confidence >= 0.7,
            "confidence": confidence,
            "votes": results
        }
