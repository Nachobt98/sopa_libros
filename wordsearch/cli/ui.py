"""Styled terminal output helpers for SopaLibros CLI commands."""

from __future__ import annotations

import time
from collections.abc import Iterable, Iterator, Sequence
from typing import TypeVar

from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

console = Console()

APP_TITLE = "SOPALIBROS · WORD SEARCH GENERATOR"
APP_SUBTITLE = "Automated KDP puzzle book generator"

PALETTE = {
    "primary": "#D6B36A",
    "accent": "#7FB3D5",
    "success": "#7DCEA0",
    "warning": "#F5B041",
    "error": "#EC7063",
    "muted": "#AAB7B8",
    "text": "#F8F9F9",
}

T = TypeVar("T")


def print_app_header(subtitle: str | None = None) -> None:
    """Print the branded application header."""
    title = Text(APP_TITLE, style=f"bold {PALETTE['primary']}")
    subtitle_text = Text(subtitle or APP_SUBTITLE, style=PALETTE["muted"])

    content = Text()
    content.append(title)
    content.append("\n")
    content.append(subtitle_text)

    console.print()
    console.print(
        Panel(
            Align.center(content),
            border_style=PALETTE["primary"],
            padding=(1, 4),
        )
    )
    console.print()


def print_section(title: str) -> None:
    """Print a compact section divider."""
    console.print()
    console.rule(f"[bold {PALETTE['primary']}]{title.upper()}[/bold {PALETTE['primary']}]")


def print_info(message: str) -> None:
    """Print a neutral informational message."""
    console.print(f"[bold {PALETTE['accent']}]•[/bold {PALETTE['accent']}] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold {PALETTE['success']}]✓[/bold {PALETTE['success']}] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold {PALETTE['warning']}]⚠[/bold {PALETTE['warning']}] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold {PALETTE['error']}]✗[/bold {PALETTE['error']}] {message}")


def print_error_panel(title: str, details: Iterable[str]) -> None:
    """Print a compact styled error panel."""
    body = "\n".join(details)
    console.print(
        Panel(
            body,
            title=Text(title, style=f"bold {PALETTE['error']}"),
            border_style=PALETTE["error"],
            padding=(1, 2),
        )
    )


def print_key_value_table(title: str, rows: Sequence[tuple[str, str]]) -> None:
    """Print a compact two-column summary table."""
    table = Table(
        title=title,
        title_style=f"bold {PALETTE['primary']}",
        border_style=PALETTE["muted"],
        header_style=f"bold {PALETTE['accent']}",
        show_lines=False,
    )
    table.add_column("Item", style=PALETTE["muted"], no_wrap=True)
    table.add_column("Value", style=PALETTE["text"])
    for key, value in rows:
        table.add_row(key, value)
    console.print(table)


def print_completion_animation() -> None:
    """Show a short terminal-only completion animation before the final panel."""
    if not console.is_terminal:
        return

    track_width = 26
    frames = [*range(0, track_width + 1, 2), *range(track_width - 2, 8, -2)]
    messages = [
        "Binding final pages",
        "Sealing production reports",
        "Preparing review handoff",
        "Book package ready",
    ]

    with Live(console=console, refresh_per_second=12, transient=True) as live:
        for index, position in enumerate(frames):
            track = ["─"] * (track_width + 1)
            track[position] = "◆"
            marker = "".join(track)
            message = messages[min(index * len(messages) // len(frames), len(messages) - 1)]
            figure = Text()
            figure.append("  ╭────╮\n", style=PALETTE["primary"])
            figure.append(f"  │ {marker} │\n", style=PALETTE["accent"])
            figure.append("  ╰────╯\n", style=PALETTE["primary"])
            figure.append(f"\n{message}...", style=f"bold {PALETTE['muted']}")
            live.update(
                Panel(
                    Align.center(Group(figure)),
                    title=Text("FINALIZING", style=f"bold {PALETTE['primary']}"),
                    border_style=PALETTE["primary"],
                    padding=(1, 4),
                )
            )
            time.sleep(0.08)
    print_success("Production package ready")


def print_completion_panel(
    *,
    title: str,
    subtitle: str,
    pdf_path: str,
    report_path: str,
    preflight_report_path: str,
    review_summary_path: str,
    recommendation: str,
) -> None:
    """Print a polished final run summary panel."""
    body = Text()
    body.append(subtitle, style=f"bold {PALETTE['success']}")
    body.append("\n\n")
    body.append("PDF", style=f"bold {PALETTE['primary']}")
    body.append(f"  {pdf_path}\n")
    body.append("Report", style=f"bold {PALETTE['primary']}")
    body.append(f"  {report_path}\n")
    body.append("Preflight", style=f"bold {PALETTE['primary']}")
    body.append(f"  {preflight_report_path}\n")
    body.append("Review", style=f"bold {PALETTE['primary']}")
    body.append(f"  {review_summary_path}\n\n")
    body.append("Recommendation: ", style=f"bold {PALETTE['accent']}")
    body.append(recommendation)

    console.print()
    console.print(
        Panel(
            Align.center(body),
            title=Text(title, style=f"bold {PALETTE['success']}"),
            border_style=PALETTE["success"],
            padding=(1, 4),
        )
    )


def create_progress() -> Progress:
    """Create the shared SopaLibros progress bar style."""
    return Progress(
        SpinnerColumn(style=PALETTE["accent"]),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(
            bar_width=34,
            complete_style=PALETTE["primary"],
            finished_style=PALETTE["success"],
            pulse_style=PALETTE["accent"],
        ),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


def track_progress(items: Iterable[T], *, description: str, total: int | None = None) -> Iterator[T]:
    """Yield items while rendering a styled progress bar."""
    resolved_total = total if total is not None else len(items) if hasattr(items, "__len__") else None
    with create_progress() as progress:
        task_id = progress.add_task(description, total=resolved_total)
        for item in items:
            yield item
            progress.update(task_id, advance=1)
