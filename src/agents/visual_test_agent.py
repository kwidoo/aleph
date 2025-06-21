from playwright.sync_api import sync_playwright
import cv2
import numpy as np
import os
from datetime import datetime
from skimage.metrics import structural_similarity as ssim
import asyncio
from agent_controller import AgentController

class VisualRegressionAgent:
    def __init__(self):
        """Initialize visual regression testing agent"""
        self.c = AgentController()
        self.screenshot_dir = os.path.expanduser("~/vue-project/tests/screenshots")
        self.baseline_dir = os.path.join(self.screenshot_dir, "baseline")
        self.current_dir = os.path.join(self.screenshot_dir, "current")
        self.diff_dir = os.path.join(self.screenshot_dir, "diff")

        # Create directories if they don't exist
        for dir_path in [self.screenshot_dir, self.baseline_dir, self.current_dir, self.diff_dir]:
            os.makedirs(dir_path, exist_ok=True)

    async def capture_component_screenshot(self, component_name, props=None, viewport=(1280, 720)):
        """Capture screenshot of a Vue component"""
        print(f"Capturing screenshot for component: {component_name}")

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": viewport[0], "height": viewport[1]}
            )
            page = context.new_page()

            # Create a simple HTML page to render the component
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

            # Create test harness HTML
            test_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>{component_name} Test</title>
              <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
              <link href="https://unpkg.com/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
              <script type="module">
                import {{ createApp }} from 'vue'
                import Component from './{component_file}'

                const app = createApp({{
                  template: `<div class="p-4">
                    <Component v-bind="props" />
                  </div>`,
                  components: {{ Component }},
                  data() {{
                    return {{
                      props: {props_str}
                    }}
                  }}
                }})

                app.mount('#app')
              </script>
            </head>
            <body>
              <div id="app"></div>
            </body>
            </html>
            """

            # Write test HTML to temporary file
            temp_html = os.path.join(self.screenshot_dir, f"{component_name}_test.html")
            with open(temp_html, "w") as f:
                f.write(test_html)

            # Navigate to the file
            page.goto(f"file://{temp_html}")

            # Wait for component to render
            page.wait_for_selector("#app")

            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(
                self.current_dir,
                f"{component_name}_{timestamp}.png"
            )
            page.screenshot(path=screenshot_path)

            # Close browser
            browser.close()

            print(f"Screenshot captured: {screenshot_path}")
            return screenshot_path

    async def compare_with_baseline(self, component_name, threshold=0.01):
        """Compare current component with baseline"""
        print(f"Comparing {component_name} with baseline")

        # Find most recent current screenshot
        current_screenshots = [
            f for f in os.listdir(self.current_dir)
            if f.startswith(f"{component_name}_")
        ]

        if not current_screenshots:
            print(f"No current screenshots found for {component_name}")
            return {"status": "error", "message": "No current screenshots found"}

        current_screenshots.sort(reverse=True)  # Most recent first
        current_path = os.path.join(self.current_dir, current_screenshots[0])

        # Find baseline screenshot
        baseline_files = [
            f for f in os.listdir(self.baseline_dir)
            if f.startswith(f"{component_name}_")
        ]

        # If no baseline exists, copy current as baseline
        if not baseline_files:
            print(f"No baseline found for {component_name}, creating one")
            baseline_path = os.path.join(
                self.baseline_dir,
                os.path.basename(current_path)
            )
            import shutil
            shutil.copy(current_path, baseline_path)
            return {"status": "baseline_created", "baseline": baseline_path}

        baseline_files.sort(reverse=True)  # Most recent first
        baseline_path = os.path.join(self.baseline_dir, baseline_files[0])

        # Compare images
        baseline_img = cv2.imread(baseline_path)
        current_img = cv2.imread(current_path)

        # Convert to grayscale
        baseline_gray = cv2.cvtColor(baseline_img, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)

        # Compute SSIM between the two images
        score, diff = self._structural_similarity(baseline_gray, current_gray)

        print(f"Similarity score: {score}")

        # If images are different
        if score < (1.0 - threshold):
            # Create diff image
            diff_path = os.path.join(
                self.diff_dir,
                f"{component_name}_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )

            # Threshold the difference image
            diff = (diff * 255).astype("uint8")
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            # Highlight differences
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]

            # Create highlight image
            highlight_img = current_img.copy()
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(highlight_img, (x, y), (x + w, y + h), (0, 0, 255), 2)

            cv2.imwrite(diff_path, highlight_img)

            # Generate AI analysis of differences
            report = await self._generate_visual_diff_report(component_name, score, diff_path)

            return {
                "status": "diff_detected",
                "score": score,
                "diff_path": diff_path,
                "report": report
            }

        return {"status": "match", "score": score}

    def _structural_similarity(self, img1, img2):
        """Calculate structural similarity index"""
        # Ensure images are the same size
        h1, w1 = img1.shape
        h2, w2 = img2.shape

        if h1 != h2 or w1 != w2:
            # Resize if needed
            img2 = cv2.resize(img2, (w1, h1))

        # Compute SSIM
        return ssim(img1, img2, full=True)

    async def _generate_visual_diff_report(self, component_name, score, diff_path):
        """Generate AI analysis of visual differences"""
        print(f"Generating visual diff report for {component_name}")

        prompt = f"""
        Analyze the visual differences detected in component {component_name}.

        Similarity score: {score:.4f}
        Diff image: {diff_path}

        Provide:
        1. Analysis of what changed
        2. Possible reasons for the change
        3. Whether the change is likely intended or a regression
        4. Recommendations for next steps
        5. Ensure <script> comes before <template>, avoid <style> unless necessary, and place all type definitions in ./types folder.
        """

        report = await self.c.c.complete(prompt, max_tokens=500)
        return report

    async def visual_test_pipeline(self):
        """Run visual tests for all components"""
        print("Running visual regression test pipeline")

        # Find all Vue components
        component_dir = os.path.expanduser("~/vue-project/src/components")
        if not os.path.exists(component_dir):
            print(f"Component directory not found: {component_dir}")
            return {"status": "error", "message": "Component directory not found"}

        components = [
            os.path.basename(f).replace(".vue", "")
            for f in os.listdir(component_dir)
            if f.endswith(".vue")
        ]

        # Test each component
        results = {}
        for component in components:
            print(f"Testing component: {component}")
            await self.capture_component_screenshot(component)
            result = await self.compare_with_baseline(component)
            results[component] = result

        # Generate summary report
        summary = await self._generate_summary_report(results)

        print("Visual test pipeline complete")
        return {
            "results": results,
            "summary": summary
        }

    async def _generate_summary_report(self, results):
        """Generate AI-powered test summary"""
        print("Generating summary report")

        # Count results by status
        status_counts = {}
        for component, result in results.items():
            status = result.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Format results for prompt
        results_summary = "\n".join([
            f"- {component}: {result.get('status', 'unknown')} " +
            f"(score: {result.get('score', 'N/A')})"
            for component, result in results.items()
        ])

        prompt = f"""
        Generate a summary report for visual regression test results:

        Total components tested: {len(results)}
        Match: {status_counts.get('match', 0)}
        Differences detected: {status_counts.get('diff_detected', 0)}
        New baselines: {status_counts.get('baseline_created', 0)}
        Errors: {status_counts.get('error', 0)}

        Component results:
        {results_summary}

        Provide:
        1. Overall assessment
        2. Components that need attention
        3. Recommended next steps
        """

        summary = await self.c.c.complete(prompt, max_tokens=800)
        return summary

if __name__ == "__main__":
    import sys

    async def main():
        agent = VisualRegressionAgent()

        if len(sys.argv) < 2:
            # Run full pipeline if no specific command
            results = await agent.visual_test_pipeline()
            print(results["summary"])
            sys.exit(0)

        command = sys.argv[1]

        if command == "capture":
            if len(sys.argv) < 3:
                print("Usage: python visual_test_agent.py capture [component_name]")
                sys.exit(1)
            await agent.capture_component_screenshot(sys.argv[2])

        elif command == "compare":
            if len(sys.argv) < 3:
                print("Usage: python visual_test_agent.py compare [component_name]")
                sys.exit(1)
            result = await agent.compare_with_baseline(sys.argv[2])
            print(result)

        elif command == "pipeline":
            results = await agent.visual_test_pipeline()
            print(results["summary"])

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    asyncio.run(main())
