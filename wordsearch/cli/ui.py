"""Styled terminal output helpers for SopaLibros CLI commands."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeVar

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
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
