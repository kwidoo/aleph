from .static_analyzer import StaticVerifier
from .runtime_validator import RuntimeValidator
from .spec_matcher import SpecMatcher
from .peer_review import PeerReviewer
import time

class VerificationPipeline:
    def __init__(self):
        self.static = StaticVerifier()
        self.runtime = RuntimeValidator()
        self.spec = SpecMatcher()
        self.peer = PeerReviewer()
        self.verification_history = []

    def verify(self, generated_code, requirements, context):
        """Execute full verification pipeline"""
        verification_id = f"verify_{int(time.time())}"
        report = {
            "id": verification_id,
            "requirements": requirements,
            "code": generated_code,
            "timestamp": time.time(),
            "results": {}
        }

        # Phase 1: Static verification
        report["results"]["static"] = self.static.full_static_check(
            generated_code,
            requirements
        )

        # Phase 2: Specification compliance
        report["results"]["spec"] = self.spec.full_spec_check(
            generated_code,
            requirements,
            requirements.get("design_url")
        )

        # Phase 3: Runtime validation
        if report["results"]["static"]["valid"]:
            report["results"]["runtime"] = self.runtime.validate_component(
                generated_code,
                requirements
            )
        else:
            report["results"]["runtime"] = {"skipped": "Static validation failed"}

        # Phase 4: Peer review
        report["results"]["peer"] = self.peer.review_code(
            generated_code,
            requirements,
            context
        )

        # Phase 5: Multi-model consensus
        report["results"]["consensus"] = self.peer.cross_model_verification(
            generated_code,
            requirements
        )

        # Calculate overall verification score
        weights = {
            "static": 0.2,
            "spec": 0.3,
            "runtime": 0.3,
            "peer": 0.15,
            "consensus": 0.05
        }

        score = 0
        for key, weight in weights.items():
            if "score" in report["results"][key]:
                score += report["results"][key]["score"] * weight
            elif "confidence" in report["results"][key]:
                score += report["results"][key]["confidence"] * weight
            elif report["results"][key].get("passed", False):
                score += weight

        report["verification_score"] = score
        report["verified"] = score >= 0.85

        # Store in history
        self.verification_history.append(report)

        return report

    def generate_corrections(self, report):
        """Generate corrected code based on verification results"""
        if report["verified"]:
            return report["code"]

        # Compile feedback from all verifiers
        feedback = "\n".join([
            f"Static Analysis: {report['results']['static'].get('error', '')}",
            f"Spec Compliance: {report['results']['spec'].get('discrepancies', '')}",
            f"Runtime Issues: {[t for t in report['results']['runtime']['test_cases'] if not t['passed']]}",
            f"Peer Review: {report['results']['peer'].get('issues', '')}"
        ])

        prompt = f"""
        Correct this code based on verification feedback:

        Original Requirements:
        {report['requirements']}

        Generated Code:
        {report['code']}

        Verification Feedback:
        {feedback}

        Provide corrected code implementing all feedback.
        """
        return self.c.complete(prompt, max_tokens=2000)

    def iterative_correction(self, generated_code, requirements, context, max_attempts=3):
        """Self-correcting verification loop"""
        for attempt in range(max_attempts):
            report = self.verify(generated_code, requirements, context)
            if report["verified"]:
                return {
                    "code": generated_code,
                    "verified": True,
                    "attempts": attempt + 1,
                    "report": report
                }

            # Generate corrections
            generated_code = self.generate_corrections(report)

        return {
            "code": generated_code,
            "verified": False,
            "attempts": max_attempts,
            "report": report
        }
