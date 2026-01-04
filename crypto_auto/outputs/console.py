from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from crypto_auto.models.analysis import ProjectAnalysis

console = Console()


def print_portfolio_analysis(projects: list[ProjectAnalysis]) -> None:
    console.print()
    console.print(Panel.fit("[bold cyan]Crypto Portfolio Analysis[/bold cyan]", border_style="cyan"))
    console.print()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Ticker", style="cyan", width=8)
    table.add_column("Price ($)", justify="right", style="white")
    table.add_column("MCap/FDV", justify="right")
    table.add_column("Dev Activity", justify="right")
    table.add_column("Health", justify="center")

    for project in projects:
        price_str = f"${project.market_data.price:,.2f}"
        ratio_str = f"{project.market_data.mcap_fdv_ratio:.1%}"

        ratio_color = _get_ratio_color(project.market_data.mcap_fdv_ratio)
        ratio_text = f"[{ratio_color}]{ratio_str}[/{ratio_color}]"

        commits_str = str(project.dev_commits_30d)
        health_emoji = _get_health_emoji(project.health_status)

        table.add_row(
            project.project.ticker,
            price_str,
            ratio_text,
            commits_str,
            health_emoji,
        )

    console.print(table)
    console.print()


def print_rebalance_recommendations(recommendations: list[dict]) -> None:
    if not recommendations:
        console.print("[green]✓ Portfolio is balanced - no purchases needed[/green]")
        console.print()
        return

    console.print(Panel.fit("[bold yellow]Rebalancing Recommendations[/bold yellow]", border_style="yellow"))
    console.print()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Ticker", style="cyan", width=8)
    table.add_column("Amount (USD)", justify="right", style="green")
    table.add_column("Price ($)", justify="right", style="white")
    table.add_column("Quantity", justify="right", style="yellow")

    for rec in recommendations:
        table.add_row(
            rec["ticker"],
            f"${rec['amount_usd']:,.2f}",
            f"${rec['current_price']:,.2f}",
            f"{rec['quantity']:.8f}",
        )

    console.print(table)
    console.print()


def print_summary_stats(projects: list[ProjectAnalysis]) -> None:
    total_mcap = sum(p.market_data.market_cap for p in projects)
    avg_fdv_ratio = sum(p.market_data.mcap_fdv_ratio for p in projects) / len(projects)
    total_commits = sum(p.dev_commits_30d for p in projects)

    warnings = [p for p in projects if p.health_status == "FDV_WARNING"]
    low_activity = [p for p in projects if p.health_status == "LOW_ACTIVITY"]

    summary = Text()
    summary.append("Summary:\n", style="bold")
    summary.append(f"  Total Market Cap: ${total_mcap:,.0f}\n", style="white")
    summary.append(f"  Average MCap/FDV Ratio: {avg_fdv_ratio:.1%}\n", style="white")
    summary.append(f"  Total Commits (30d): {total_commits}\n", style="white")

    if warnings:
        summary.append(f"  ⚠️  FDV Warnings: {len(warnings)} project(s)\n", style="yellow")
    if low_activity:
        summary.append(f"  ⚠️  Low Activity: {len(low_activity)} project(s)\n", style="yellow")

    if not warnings and not low_activity:
        summary.append("  ✅ All projects healthy\n", style="green")

    console.print(Panel(summary, border_style="blue", title="Portfolio Summary"))
    console.print()


def _get_ratio_color(ratio: float) -> str:
    if ratio < 0.4:
        return "red"
    elif ratio < 0.45:
        return "yellow"
    elif ratio <= 0.5:
        return "green"
    else:
        return "bright_green"


def _get_health_emoji(status: str) -> str:
    match status:
        case "OK":
            return "[green]✅ OK[/green]"
        case "FDV_WARNING":
            return "[red]⚠️  FDV[/red]"
        case "LOW_ACTIVITY":
            return "[yellow]⚠️  DEV[/yellow]"
        case _:
            return "[white]?[/white]"
