import rich
from rich.table import Table
from rich.panel import Panel

class VerificationDashboard:
    def display_report(self, report):
        """Display verification report in terminal"""
        console = rich.get_console()

        # Header
        status = "[green]VERIFIED[/green]" if report["verified"] else "[red]REJECTED[/red]"
        console.print(Panel(
            f"[bold]Component Verification[/bold]\n"
            f"Score: [yellow]{report['verification_score']:.2f}/1.0[/yellow] {status}",
            expand=False
        ))

        # Detailed results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Verification Stage")
        table.add_column("Status")
        table.add_column("Details")

        for stage, result in report["results"].items():
            status = "[green]PASS[/green]" if result.get("passed", result.get("verified", False)) else "[red]FAIL[/red]"
            details = self._format_details(result)
            table.add_row(stage.upper(), status, details)

        console.print(table)

        # Correction history
        if "correction_history" in report:
            console.print("\n[bold]Correction History:[/bold]")
            for i, correction in enumerate(report["correction_history"], 1):
                console.print(f"[bold]Attempt {i}:[/bold] {correction['summary']}")

    def _format_details(self, result):
        """Format result details for display"""
        if "error" in result:
            return f"[red]{result['error']}[/red]"
        if "issues" in result:
            return "\n".join([f"- [yellow]{issue}[/yellow]" for issue in result["issues"]])
        if "test_cases" in result:
            passed = sum(1 for t in result["test_cases"] if t["passed"])
            return f"[green]{passed}/{len(result['test_cases'])} tests passed[/green]"
        if "score" in result:
            return f"Score: [yellow]{result['score']:.2f}[/yellow]"
        return "No details available"
