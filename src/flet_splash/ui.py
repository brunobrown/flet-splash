"""Rich-based UI helpers for flet-splash CLI output."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

theme = Theme(
    {
        "success": "bold green",
        "error": "bold red",
        "info": "bold cyan",
        "highlight": "bold magenta",
        "muted": "dim",
        "warning": "bold yellow",
    }
)

console = Console(theme=theme)


# ---------------------------------------------------------------------------
# Panels
# ---------------------------------------------------------------------------


def header_panel(subtitle: str = "") -> None:
    content = f"[info]{subtitle}[/info]" if subtitle else ""
    console.print()
    console.print(
        Panel(
            content,
            title="[highlight]Flet Splash[/highlight]",
            border_style="bright_blue",
        )
    )


def success_panel(build_type: str, output_dir: str | None, next_steps: list[str]) -> None:
    lines: list[str] = []

    if output_dir:
        lines.append(f"  [muted]Output:[/muted] {output_dir}")

    if next_steps:
        lines.append("")
        lines.append("  [info]Next steps:[/info]")
        for s in next_steps:
            lines.append(f"    [muted]{s}[/muted]")

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title="[success]Build Successful[/success]",
            border_style="green",
        )
    )


def error_panel(title: str, body: str) -> None:
    console.print()
    console.print(Panel(body, title=f"[error]{title}[/error]", border_style="red"))


def failure_panel(tips: list[str]) -> None:
    lines = ["  Check the error messages above for details."]

    if tips:
        lines.append("")
        lines.append("  [info]Tips:[/info]")
        for tip in tips:
            lines.append(f"    [muted]{tip}[/muted]")

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title="[error]Build Failed[/error]",
            border_style="red",
        )
    )


def info_panel(title: str, content: str) -> None:
    console.print()
    console.print(Panel(content, title=f"[info]{title}[/info]", border_style="cyan"))


# ---------------------------------------------------------------------------
# Config table
# ---------------------------------------------------------------------------


def config_table(rows: list[tuple[str, str]]) -> None:
    table = Table(
        show_header=False,
        padding=(0, 2),
        border_style="bright_blue",
        box=None,
    )
    table.add_column("Key", style="info", min_width=16)
    table.add_column("Value")

    for key, value in rows:
        table.add_row(key, value)

    console.print()
    console.print(table)


# ---------------------------------------------------------------------------
# Inline messages
# ---------------------------------------------------------------------------


def step(n: int, total: int, msg: str) -> None:
    console.print(f"\n  [highlight]Step {n}/{total}[/highlight]  {msg}\n")


def modified(msg: str) -> None:
    console.print(f"    [success]{msg}[/success]")


def warning(msg: str) -> None:
    console.print(f"    [warning]{msg}[/warning]")


def info(label: str, value: str) -> None:
    console.print(f"  [info]{label}:[/info] {value}")


def build_info(msg: str) -> None:
    console.print(f"\n  [highlight]{msg}[/highlight]\n")
