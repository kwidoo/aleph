import os
import json
import asyncio
from playwright.sync_api import sync_playwright
from agent_controller import AgentController

class AccessibilityAgent:
    """Agent for automated accessibility audits of Vue components"""

    WCAG_VERSIONS = ["wcag21a", "wcag21aa", "wcag22a", "wcag22aa"]

    def __init__(self):
        """Initialize accessibility agent"""
        self.c = AgentController()
        self.results_dir = os.path.expanduser("~/vue-project/tests/accessibility")
        os.makedirs(self.results_dir, exist_ok=True)

    async def audit_component(self, component_name, props=None, standard="wcag21aa"):
        """Run accessibility audit on component"""
        print(f"Auditing component: {component_name} against {standard}")

        if standard not in self.WCAG_VERSIONS:
            print(f"Unsupported standard: {standard}. Using wcag21aa instead.")
            standard = "wcag21aa"

        # Create test harness HTML for the component
        component_file = f"src/components/{component_name}.vue"

        # Generate component props
        props_str = "{}"
        if props:
            props_str = "{"
            for key, value in props.items():
                if isinstance(value, str):
                    props_str += f"{key}: '{value}', "
                else:
                    props_str += f"{key}: {value}, "
            props_str += "}"

        # Create HTML file with axe-core for accessibility testing
        test_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>{component_name} Accessibility Test</title>
          <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
          <link href="https://unpkg.com/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
          <script src="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js"></script>
          <script type="module">
            import {{ createApp }} from 'vue'
            import Component from './{component_file}'

            window.auditResults = null;
            window.auditComplete = false;

            const app = createApp({{
              template: `<div class="p-4">
                <Component v-bind="props" />
              </div>`,
              components: {{ Component }},
              data() {{
                return {{
                  props: {props_str}
                }}
              }},
              mounted() {{
                // Run accessibility audit after component is mounted
                setTimeout(() => {{
                  axe.run(document.body, {{
                    runOnly: {{
                      type: 'tag',
                      values: ['{standard}']
                    }}
                  }}).then(results => {{
                    window.auditResults = results;
                    window.auditComplete = true;
                  }}).catch(err => {{
                    console.error('Error running accessibility audit:', err);
                    window.auditError = err.toString();
                    window.auditComplete = true;
                  }});
                }}, 500);
              }}
            }});

            app.mount('#app');
          </script>
        </head>
        <body>
          <div id="app" role="main"></div>
        </body>
        </html>
        """

        # Write test file
        test_path = os.path.join(self.results_dir, f"{component_name}_a11y_test.html")
        with open(test_path, "w") as f:
            f.write(test_html)

        results = {}

        # Run accessibility audit with Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Navigate to test page
            page.goto(f"file://{test_path}")

            # Wait for audit to complete
            try:
                page.wait_for_function("window.auditComplete === true", timeout=30000)

                # Get audit results
                audit_results = page.evaluate("() => window.auditResults")
                audit_error = page.evaluate("() => window.auditError")

                if audit_error:
                    results = {
                        "error": audit_error,
                        "status": "error"
                    }
                else:
                    results = audit_results
            except Exception as e:
                print(f"Error running accessibility audit: {e}")
                results = {
                    "error": str(e),
                    "status": "error"
                }

            browser.close()

        # Save results
        result_path = os.path.join(self.results_dir, f"{component_name}_a11y_results.json")
        with open(result_path, "w") as f:
            json.dump(results, f, indent=2)

        # Generate accessibility report
        report = await self._generate_accessibility_report(results)

        print(f"Accessibility audit complete for {component_name}")
        return {
            "results": results,
            "report": report,
            "result_path": result_path,
            "violations_count": len(results.get("violations", [])),
            "passes_count": len(results.get("passes", []))
        }

    async def _generate_accessibility_report(self, audit_results):
        """Generate AI analysis of accessibility issues"""
        print("Generating accessibility report")

        if "error" in audit_results:
            return f"Error running accessibility audit: {audit_results['error']}"

        # Format violations for the prompt
        violations = audit_results.get("violations", [])
        violations_text = ""

        for i, violation in enumerate(violations[:10]):  # Limit to 10 violations for prompt length
            violations_text += f"{i+1}. {violation.get('id', 'Unknown')} - {violation.get('description', 'No description')}\n"
            violations_text += f"   Impact: {violation.get('impact', 'unknown')}\n"
            violations_text += f"   Help: {violation.get('help', 'No help available')}\n"
            violations_text += f"   Occurrences: {len(violation.get('nodes', []))}\n\n"

        if not violations:
            violations_text = "No accessibility violations detected."

        # Get pass count by category
        passes = audit_results.get("passes", [])
        passes_count = len(passes)

        prompt = f"""
        Analyze the accessibility audit results for a Vue component:

        Summary:
        - Total violations: {len(violations)}
        - Tests passed: {passes_count}

        Violations:
        {violations_text}

        Provide:
        1. Summary of accessibility compliance
        2. Explanation of the most critical issues
        3. Recommendations for fixing the issues
        4. Best practices for ensuring accessibility in Vue components
        """

        report = await self.c.c.complete(prompt, max_tokens=1000)
        return report

    async def generate_accessibility_report(self, component_name, audit_results):
        """Generate a detailed accessibility report"""
        print(f"Generating accessibility report for {component_name}")

        # Metrics
        metrics = {
            "violations_count": len(audit_results.get("violations", [])),
            "passes_count": len(audit_results.get("passes", [])),
            "incomplete_count": len(audit_results.get("incomplete", []))
        }

        # Suggestions
        suggestions = [
            "Ensure all interactive elements have ARIA roles.",
            "Use semantic HTML wherever possible.",
            "Provide descriptive labels for all form elements."
        ]

        # Issues
        issues = [
            f"{violation['id']}: {violation['description']}"
            for violation in audit_results.get("violations", [])
        ]

        # Overall score (placeholder logic)
        overall_score = max(0, 1 - (metrics["violations_count"] * 0.1))

        # Report structure
        report = {
            "component_name": component_name,
            "metrics": metrics,
            "suggestions": suggestions,
            "issues": issues,
            "overall_score": overall_score
        }

        # Export report to JSON
        report_path = os.path.join(self.results_dir, f"{component_name}_accessibility_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Accessibility report generated: {report_path}")
        return report

    async def fix_accessibility_issues(self, component_name, audit_results=None):
        """Automatically fix accessibility issues"""
        print(f"Fixing accessibility issues for {component_name}")

        # Get component code
        component_path = f"src/components/{component_name}.vue"
        with open(component_path, "r") as f:
            original_code = f.read()

        # Run audit if not provided
        if not audit_results:
            audit = await self.audit_component(component_name)
            audit_results = audit["results"]

        violations = audit_results.get("violations", [])
        original_issues = len(violations)

        if not violations:
            print(f"No accessibility issues found in {component_name}")
            return {
                "status": "no_issues",
                "original_issues": 0,
                "fixed_issues": 0
            }

        # Format violations for the prompt
        violations_text = ""
        for i, violation in enumerate(violations):
            violations_text += f"{i+1}. {violation.get('id', 'Unknown')} - {violation.get('description', 'No description')}\n"
            violations_text += f"   Impact: {violation.get('impact', 'unknown')}\n"
            violations_text += f"   Help: {violation.get('help', 'No help available')}\n"

            # Include specific element issues
            for j, node in enumerate(violation.get('nodes', [])[:3]):  # Limit to 3 examples per violation
                violations_text += f"   Element {j+1}: {node.get('html', 'Unknown element')}\n"
                if "failureSummary" in node:
                    violations_text += f"   Failure: {node.get('failureSummary', '')}\n"

            violations_text += "\n"

        # Generate fixed code
        prompt = f"""
        Fix accessibility issues in this Vue component:

        Original code:
        ```vue
        {original_code}
        ```

        Accessibility issues ({len(violations)}):
        {violations_text}

        Provide a corrected version of the component that fixes all accessibility issues.
        Make only the necessary changes to address the specific accessibility problems.
        Maintain all functionality and styling while making the component accessible.
        """

        fixed_code = await self.c.c.complete(prompt, max_tokens=2500)

        # Create temporary file for testing the fix
        temp_component_path = f"src/components/{component_name}_a11y_fixed.vue"
        with open(temp_component_path, "w") as f:
            f.write(fixed_code)

        # Re-run audit to verify fix
        fixed_audit = await self.audit_component(f"{component_name}_a11y_fixed")
        fixed_violations = fixed_audit["results"].get("violations", [])
        fixed_issues = original_issues - len(fixed_violations)

        # Generate compliance report
        compliance_report = await self._generate_compliance_report(
            original_issues,
            len(fixed_violations),
            component_name
        )

        # If fixes were effective, apply to original component
        if len(fixed_violations) < original_issues:
            print(f"Fixed {fixed_issues} accessibility issues in {component_name}")
            with open(component_path, "w") as f:
                f.write(fixed_code)
        else:
            print(f"No improvements made to {component_name}")

        # Clean up temporary file
        os.remove(temp_component_path)

        return {
            "status": "fixed" if fixed_issues > 0 else "no_improvement",
            "original_issues": original_issues,
            "fixed_issues": fixed_issues,
            "remaining_issues": len(fixed_violations),
            "report": compliance_report
        }

    async def _generate_compliance_report(self, original_issues, remaining_issues, component_name):
        """Generate AI compliance report"""
        print("Generating compliance report")

        fixed_issues = original_issues - remaining_issues
        fix_percentage = (fixed_issues / original_issues * 100) if original_issues > 0 else 0

        prompt = f"""
        Generate an accessibility compliance report for component '{component_name}':

        - Original accessibility issues: {original_issues}
        - Issues fixed: {fixed_issues} ({fix_percentage:.1f}%)
        - Remaining issues: {remaining_issues}

        Provide:
        1. Assessment of the accessibility improvements
        2. Recommendations for addressing any remaining issues
        3. Best practices to prevent similar issues in future components
        4. Compliance status with WCAG standards
        """

        report = await self.c.c.complete(prompt, max_tokens=800)
        return report

    async def monitor_accessibility(self):
        """Continuous accessibility monitoring"""
        print("Starting accessibility monitoring")

        # Find all Vue components
        component_dir = os.path.expanduser("~/vue-project/src/components")
        if not os.path.exists(component_dir):
            print(f"Component directory not found: {component_dir}")
            return {
                "status": "error",
                "message": "Component directory not found"
            }

        components = [
            os.path.basename(f).replace(".vue", "")
            for f in os.listdir(component_dir)
            if f.endswith(".vue")
        ]

        results = {}
        components_with_issues = []

        # Audit each component
        for component in components:
            print(f"Monitoring component: {component}")
            audit = await self.audit_component(component)
            results[component] = {
                "violations_count": audit["violations_count"],
                "passes_count": audit["passes_count"]
            }

            if audit["violations_count"] > 0:
                components_with_issues.append(component)

        # Fix issues automatically
        if components_with_issues:
            print(f"Found {len(components_with_issues)} components with accessibility issues")
            for component in components_with_issues:
                await self.fix_accessibility_issues(component)

        return {
            "status": "completed",
            "components_audited": len(components),
            "components_with_issues": len(components_with_issues),
            "results": results
        }

    async def suggest_aria_attributes(self, component_name):
        """Suggest ARIA attributes for a component"""
        print(f"Suggesting ARIA attributes for {component_name}")

        # Analyze component structure and functionality
        # Placeholder logic for ARIA suggestions
        aria_suggestions = {
            "role": "button",
            "aria-label": "Descriptive label for the component",
            "aria-hidden": "false"
        }

        print(f"ARIA suggestions for {component_name}: {aria_suggestions}")
        return aria_suggestions

    async def validate_wcag_compliance(self, component_name, level="AA"):
        """Validate WCAG compliance for a component"""
        print(f"Validating WCAG {level} compliance for {component_name}")

        if level not in ["A", "AA", "AAA"]:
            print(f"Unsupported WCAG level: {level}. Defaulting to AA.")
            level = "AA"

        # Placeholder logic for WCAG validation
        compliance_results = {
            "compliant": True,
            "issues": []
        }

        print(f"WCAG {level} compliance results for {component_name}: {compliance_results}")
        return compliance_results

if __name__ == "__main__":
    import sys

    async def main():
        agent = AccessibilityAgent()

        if len(sys.argv) < 2:
            print("Usage: python accessibility_agent.py [command] [component_name]")
            sys.exit(1)

        command = sys.argv[1]

        if command == "audit":
            if len(sys.argv) < 3:
                print("Usage: python accessibility_agent.py audit [component_name]")
                sys.exit(1)

            result = await agent.audit_component(sys.argv[2])
            print(f"Violations: {result['violations_count']}")
            print(result["report"])

        elif command == "fix":
            if len(sys.argv) < 3:
                print("Usage: python accessibility_agent.py fix [component_name]")
                sys.exit(1)

            result = await agent.fix_accessibility_issues(sys.argv[2])
            print(f"Fixed {result['fixed_issues']} of {result['original_issues']} issues")
            print(result["report"])

        elif command == "monitor":
            result = await agent.monitor_accessibility()
            print(f"Audited {result['components_audited']} components")
            print(f"Found issues in {result['components_with_issues']} components")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    asyncio.run(main())
