import difflib
from continue.api import Continue
from knowledge_manager import KnowledgeHub

class SpecMatcher:
    def __init__(self):
        self.c = Continue()
        self.knowledge = KnowledgeHub()

    def structural_similarity(self, generated, reference):
        """Compare code structure"""
        gen_lines = generated.splitlines()
        ref_lines = reference.splitlines()

        sm = difflib.SequenceMatcher(None, gen_lines, ref_lines)
        return sm.ratio()

    def requirement_coverage(self, generated, requirements):
        """Check requirement coverage"""
        prompt = f"""
        Verify if this code meets all requirements:

        Requirements:
        {requirements}

        Code:
        {generated}

        Return JSON:
        {{
            "covered": ["requirement1", "requirement2"],
            "missing": ["requirement3"],
            "score": 0.85
        }}
        """
        return self.c.complete(prompt, format="json")

    def check_against_design(self, generated, design_url):
        """Compare with design specification"""
        design_spec = self.knowledge.query_design(design_url)
        prompt = f"""
        Compare this Vue component code with its design specification:

        Design Specs:
        {design_spec}

        Generated Code:
        {generated}

        Identify discrepancies and return JSON:
        {{
            "matches": true/false,
            "discrepancies": ["Element X missing", "Color mismatch"],
            "similarity_score": 0.92
        }}
        """
        return self.c.complete(prompt, format="json")

    def full_spec_check(self, generated, requirements, design_url=None):
        """Comprehensive specification check"""
        report = {
            "requirement_coverage": self.requirement_coverage(generated, requirements),
            "design_match": self.check_against_design(generated, design_url) if design_url else None
        }

        # Calculate overall score
        req_score = report["requirement_coverage"]["score"]
        design_score = report["design_match"]["similarity_score"] if design_url else 1.0
        report["overall_score"] = (req_score + design_score) / (2 if design_url else 1)

        report["passed"] = report["overall_score"] >= 0.85
        return report
