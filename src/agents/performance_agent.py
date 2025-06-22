from playwright.sync_api import sync_playwright
import time
import json
import matplotlib.pyplot as plt
import os
import numpy as np
from agent_controller import AgentController
import asyncio

class PerformanceAgent:
    def __init__(self):
        """Initialize performance benchmarking agent"""
        self.c = AgentController()
        self.results_dir = os.path.expanduser("~/vue-project/tests/performance")
        os.makedirs(self.results_dir, exist_ok=True)

    async def benchmark_component(self, component_name, props=None, iterations=50):
        """Benchmark component rendering performance"""
        print(f"Benchmarking component: {component_name} with {iterations} iterations")

        metrics = {
            'mount_time': [],
            'update_time': [],
            'memory_usage': []
        }

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch()
            context = browser.new_context()

            for i in range(iterations):
                page = context.new_page()

                # Create test harness
                component_file = f"src/components/{component_name}.vue"

                # Generate prop variations for update testing
                props_str = "{}"
                if props:
                    props_str = "{"
                    for key, value in props.items():
                        if isinstance(value, str):
                            props_str += f"{key}: '{value}', "
                        else:
                            props_str += f"{key}: {value}, "
                    props_str += "}"

                # Create HTML file with performance measurement code
                test_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                  <meta charset="UTF-8">
                  <title>{component_name} Performance Test</title>
                  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
                  <script src="https://unpkg.com/tailwindcss@2.2.19/dist/tailwind.min.css"></script>
                  <script type="module">
                    import {{ createApp }} from 'vue'
                    import Component from './{component_file}'

                    window.metrics = {{}};

                    // Mount time measurement
                    performance.mark('mount-start');

                    const app = createApp({{
                      template: `<div class="p-4">
                        <Component ref="component" v-bind="props" @update="updateComponent" />
                      </div>`,
                      components: {{ Component }},
                      data() {{
                        return {{
                          props: {props_str}
                        }}
                      }},
                      mounted() {{
                        performance.mark('mount-end');
                        const measure = performance.measure('mount', 'mount-start', 'mount-end');
                        window.metrics.mountTime = measure.duration;

                        // Measure update time after a short delay
                        setTimeout(() => {{
                          this.updateComponent();
                        }}, 500);
                      }},
                      methods: {{
                        updateComponent() {{
                          // Update time measurement
                          performance.mark('update-start');
                          const newProps = JSON.parse(JSON.stringify(this.props));
                          // Modify a prop to trigger update
                          const keys = Object.keys(newProps);
                          if (keys.length > 0) {{
                            const key = keys[0];
                            if (typeof newProps[key] === 'string') {{
                              newProps[key] = newProps[key] + ' (updated)';
                            }} else if (typeof newProps[key] === 'number') {{
                              newProps[key] = newProps[key] + 1;
                            }}
                          }}
                          this.props = newProps;

                          this.$nextTick(() => {{
                            performance.mark('update-end');
                            const measure = performance.measure('update', 'update-start', 'update-end');
                            window.metrics.updateTime = measure.duration;

                            // Measure memory (if available)
                            if (performance.memory) {{
                              window.metrics.memoryUsage = performance.memory.usedJSHeapSize;
                            }}

                            // Report results
                            window.reportComplete = true;
                          }});
                        }}
                      }}
                    }});

                    app.mount('#app');
                  </script>
                </head>
                <body>
                  <div id="app"></div>
                </body>
                </html>
                """

                # Write test file
                test_path = os.path.join(self.results_dir, f"{component_name}_perf_test.html")
                with open(test_path, "w") as f:
                    f.write(test_html)

                # Navigate to test page
                page.goto(f"file://{test_path}")

                # Wait for test to complete
                page.wait_for_function("window.reportComplete === true", timeout=10000)

                # Get metrics
                results = page.evaluate("() => window.metrics")

                # Store results
                if 'mountTime' in results:
                    metrics['mount_time'].append(results['mountTime'])

                if 'updateTime' in results:
                    metrics['update_time'].append(results['updateTime'])

                if 'memoryUsage' in results:
                    metrics['memory_usage'].append(results['memoryUsage'])

                # Close page
                page.close()

                if i % 10 == 0:
                    print(f"Completed {i}/{iterations} iterations")

            # Close browser
            browser.close()

        # Calculate statistics
        stats = self._calculate_statistics(metrics)

        # Save results
        result_path = os.path.join(self.results_dir, f"{component_name}_results.json")
        with open(result_path, "w") as f:
            json.dump({
                "metrics": metrics,
                "stats": stats,
                "component": component_name,
                "iterations": iterations
            }, f, indent=2)

        # Generate visualizations
        plot_path = await self.visualize_metrics(metrics, component_name)

        # Generate AI report
        report = await self._generate_performance_report(component_name, stats)

        print(f"Benchmark complete for {component_name}")
        return {
            "metrics": metrics,
            "stats": stats,
            "report": report,
            "result_path": result_path,
            "plot_path": plot_path
        }

    def _calculate_statistics(self, metrics):
        """Calculate statistics from metrics"""
        stats = {}

        for metric_name, values in metrics.items():
            if values:
                stats[metric_name] = {
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "p95": np.percentile(values, 95),
                    "min": np.min(values),
                    "max": np.max(values),
                    "std": np.std(values)
                }

        return stats

    async def _generate_performance_report(self, component_name, metrics):
        """Generate AI analysis of performance metrics"""
        print(f"Generating performance report for {component_name}")

        # Format metrics for prompt
        metrics_text = ""
        for metric_name, stats in metrics.items():
            metrics_text += f"{metric_name}:\n"
            for stat_name, value in stats.items():
                metrics_text += f"  - {stat_name}: {value:.2f}\n"

        prompt = f"""
        Analyze the performance metrics for Vue component {component_name}:

        {metrics_text}

        Provide:
        1. Overall assessment of component performance
        2. Specific areas of concern (if any)
        3. Recommendations for optimization
        4. Context for these metrics (are they good/average/poor)
        5. Ensure <script> comes before <template>, avoid <style> unless necessary, and place all type definitions in ./types folder.
        """

        report = await self.c.c.complete(prompt, max_tokens=700)
        return report

    async def visualize_metrics(self, metrics, component_name):
        """Generate visualization of performance metrics"""
        print(f"Creating visualizations for {component_name}")

        # Create figure with subplots
        fig, axs = plt.subplots(len(metrics), 1, figsize=(10, 4 * len(metrics)))

        # If only one metric, axs is not an array
        if len(metrics) == 1:
            axs = [axs]

        # Plot each metric
        for i, (metric_name, values) in enumerate(metrics.items()):
            if values:
                axs[i].hist(values, bins=20)
                axs[i].set_title(f"{component_name}: {metric_name}")
                axs[i].set_xlabel("Milliseconds" if "time" in metric_name.lower() else "Bytes")
                axs[i].set_ylabel("Frequency")

                # Add statistics
                mean = np.mean(values)
                median = np.median(values)
                p95 = np.percentile(values, 95)

                axs[i].axvline(mean, color='r', linestyle='--', label=f'Mean: {mean:.2f}')
                axs[i].axvline(median, color='g', linestyle='--', label=f'Median: {median:.2f}')
                axs[i].axvline(p95, color='b', linestyle='--', label=f'95th %: {p95:.2f}')
                axs[i].legend()

        plt.tight_layout()

        # Save plot
        plot_path = os.path.join(self.results_dir, f"{component_name}_performance.png")
        plt.savefig(plot_path)
        plt.close()

        return plot_path

    async def optimize_component(self, component_name):
        """Automatically optimize component performance"""
        print(f"Optimizing performance for component: {component_name}")

        # Get original component
        component_path = f"src/components/{component_name}.vue"
        with open(component_path, "r") as f:
            original_code = f.read()

        # Run initial benchmark
        original_benchmark = await self.benchmark_component(component_name, iterations=25)

        # Generate optimized version
        prompt = f"""
        Optimize this Vue component for performance:

        {original_code}

        Current performance metrics:
        - Mount time: {original_benchmark['stats']['mount_time']['mean']:.2f}ms average
        - Update time: {original_benchmark['stats']['update_time']['mean']:.2f}ms average

        Apply these optimization techniques:
        1. Use v-once for static content
        2. Avoid expensive operations in computed properties
        3. Use functional components where appropriate
        4. Optimize v-for loops with key and avoid inline handlers
        5. Consider using shallowRef for large objects
        6. Use proper memoization with computed properties
        7. Ensure efficient prop handling
        """

        optimized_code = await self.c.c.complete(prompt, max_tokens=2000)

        # Create temporary optimized component
        optimized_path = component_path.replace(".vue", ".optimized.vue")
        with open(optimized_path, "w") as f:
            f.write(optimized_code)

        # Benchmark optimized version (use a copy of the original for testing)
        # For this example, we'll copy it to the components directory
        temp_component_path = f"src/components/{component_name}_optimized.vue"
        with open(temp_component_path, "w") as f:
            f.write(optimized_code)

        # Run benchmark on optimized version
        optimized_benchmark = await self.benchmark_component(f"{component_name}_optimized", iterations=25)

        # Clean up temporary component
        os.remove(temp_component_path)

        # Compare results and generate report
        comparison = await self._generate_comparison_report(
            original_benchmark["stats"],
            optimized_benchmark["stats"]
        )

        # Decide whether to apply optimization
        improvement_threshold = 0.1  # 10% improvement
        mount_improvement = 1.0 - (
            optimized_benchmark["stats"]["mount_time"]["mean"] /
            original_benchmark["stats"]["mount_time"]["mean"]
        )

        update_improvement = 1.0 - (
            optimized_benchmark["stats"]["update_time"]["mean"] /
            original_benchmark["stats"]["update_time"]["mean"]
        )

        if mount_improvement >= improvement_threshold or update_improvement >= improvement_threshold:
            print(f"Performance improved! Applying optimizations to {component_name}")
            with open(component_path, "w") as f:
                f.write(optimized_code)

            return {
                "applied": True,
                "original": original_benchmark["stats"],
                "optimized": optimized_benchmark["stats"],
                "mount_improvement": mount_improvement,
                "update_improvement": update_improvement,
                "report": comparison
            }
        else:
            print(f"Insufficient performance improvement for {component_name}")
            return {
                "applied": False,
                "original": original_benchmark["stats"],
                "optimized": optimized_benchmark["stats"],
                "mount_improvement": mount_improvement,
                "update_improvement": update_improvement,
                "report": comparison
            }

    async def _generate_comparison_report(self, original, optimized):
        """Generate AI comparison report"""
        print("Generating optimization comparison report")

        # Format metrics for the prompt
        comparison_text = ""
        for metric_name in original:
            if metric_name in optimized:
                orig_mean = original[metric_name]["mean"]
                opt_mean = optimized[metric_name]["mean"]
                diff_pct = (1.0 - (opt_mean / orig_mean)) * 100

                comparison_text += f"{metric_name}:\n"
                comparison_text += f"  - Original: {orig_mean:.2f}ms\n"
                comparison_text += f"  - Optimized: {opt_mean:.2f}ms\n"
                comparison_text += f"  - Difference: {diff_pct:.1f}%\n"

        prompt = f"""
        Compare the performance before and after optimization:

        {comparison_text}

        Provide:
        1. Analysis of the improvements
        2. Which optimizations were most effective
        3. Further optimization opportunities
        4. Whether the optimization was worthwhile
        """

        report = await self.c.c.complete(prompt, max_tokens=700)
        return report

    async def test_responsive_design(self, component_name, breakpoints):
        """Test responsive design for a Vue component across breakpoints"""
        print(f"Testing responsive design for: {component_name}")

        results = {}

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()

            for breakpoint in breakpoints:
                page = context.new_page()
                page.set_viewport_size(breakpoint)

                component_file = f"src/components/{component_name}.vue"
                page.goto(f"file://{os.path.abspath(component_file)}")

                # Capture screenshot for visual validation
                screenshot_path = os.path.join(self.results_dir, f"{component_name}_{breakpoint['width']}x{breakpoint['height']}.png")
                page.screenshot(path=screenshot_path)

                # Collect performance metrics
                metrics = page.evaluate("() => ({
                    layoutShift: performance.getEntriesByType('layout-shift'),
                    paintTiming: performance.getEntriesByType('paint')
                })")

                results[f"{breakpoint['width']}x{breakpoint['height']}"] = metrics

            browser.close()

        # Save results to a JSON file
        results_file = os.path.join(self.results_dir, f"{component_name}_responsive_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=4)

        print(f"Responsive design test results saved to {results_file}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python performance_agent.py [command] [component_name]")
        print("Commands: benchmark, optimize, responsive")
        sys.exit(1)

    command = sys.argv[1]
    component_name = sys.argv[2]

    agent = PerformanceAgent()

    if command == "benchmark":
        asyncio.run(agent.benchmark_component(component_name))
    elif command == "optimize":
        print("Optimization not yet implemented.")
    elif command == "responsive":
        asyncio.run(agent.test_responsive_design(component_name))
    else:
        print(f"Unknown command: {command}")
        print("Commands: benchmark, optimize, responsive")
