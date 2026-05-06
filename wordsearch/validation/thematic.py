"""
Validation helpers for thematic word search books.

The goal is to fail early before rendering pages, because page numbering and
"Solution on page X" references depend on every puzzle being viable.
"""

from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass, field
from typing import Sequence

from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.text_normalization import normalize_word_for_grid

REPORT_WIDTH = 100
BULLET_INDENT = "  - "
CONTINUATION_INDENT = "    "


@dataclass
class ValidationIssue:
    severity: str
    message: str
    puzzle_index: int | None = None
    puzzle_title: str | None = None
    context: str | None = None

    def format(self) -> str:
        prefix = "ERROR" if self.severity == "error" else "WARNING"

        if self.context:
            return f"[{prefix}] {self.context}: {self.message}"

        if self.puzzle_index is not None:
            title = f" - {self.puzzle_title}" if self.puzzle_title else ""
            return f"[{prefix}] Puzzle {self.puzzle_index + 1}{title}: {self.message}"

        return f"[{prefix}] {self.message}"


def _print_wrapped_issue(issue: ValidationIssue) -> None:
    """Print one validation issue with stable indentation in narrow terminals."""
    wrapped = textwrap.fill(
        issue.format(),
        width=REPORT_WIDTH,
        initial_indent=BULLET_INDENT,
        subsequent_indent=CONTINUATION_INDENT,
        break_long_words=False,
        break_on_hyphens=False,
    )
    print(wrapped)


@dataclass
class ThematicValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def add_error(
        self,
        message: str,
        puzzle: PuzzleSpec | None = None,
        *,
        context: str | None = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity="error",
                message=message,
                puzzle_index=puzzle.index if puzzle else None,
                puzzle_title=puzzle.title if puzzle else None,
                context=context,
            )
        )

    def add_warning(
        self,
        message: str,
        puzzle: PuzzleSpec | None = None,
        *,
        context: str | None = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity="warning",
                message=message,
                puzzle_index=puzzle.index if puzzle else None,
                puzzle_title=puzzle.title if puzzle else None,
                context=context,
            )
        )

    def print_summary(self) -> None:
        print("\n=== Informe de validación ===")

        if not self.issues:
            print("OK: no se han encontrado problemas de validación.")
            return

        if self.errors:
            print(f"\nERRORES BLOQUEANTES ({len(self.errors)}):")
            for issue in self.errors:
                _print_wrapped_issue(issue)
        else:
            print("\nERRORES BLOQUEANTES: ninguno.")

        if self.warnings:
            print(f"\nAVISOS NO BLOQUEANTES ({len(self.warnings)}):")
            for issue in self.warnings:
                _print_wrapped_issue(issue)
        else:
            print("\nAVISOS NO BLOQUEANTES: ninguno.")

        print(f"\nResumen: {len(self.errors)} error(es), {len(self.warnings)} aviso(s).")

        if self.errors:
            print("Resultado: la generación se detendrá para evitar un PDF con paginación incorrecta.")
        else:
            print("Resultado: se puede continuar con la generación del libro.")


def validate_thematic_specs(
    specs: Sequence[PuzzleSpec],
    grid_size: int,
    *,
    min_words_per_puzzle: int = 1,
    max_fact_chars_warning: int = 260,
    check_background_files: bool = True,
) -> ThematicValidationReport:
    """
    Validate parsed thematic puzzle specs before any rendering happens.

    Errors stop generation. Warnings are informative and do not stop generation.
    """
    report = ThematicValidationReport()

    if not specs:
        report.add_error("No se ha encontrado ningún puzzle en el archivo temático.")
        return report

    warned_backgrounds: set[str] = set()

    for spec in specs:
        _validate_single_spec(
            spec,
            grid_size,
            report,
            min_words_per_puzzle=min_words_per_puzzle,
            max_fact_chars_warning=max_fact_chars_warning,
            check_background_files=check_background_files,
            warned_backgrounds=warned_backgrounds,
        )

    return report


def _validate_single_spec(
    spec: PuzzleSpec,
    grid_size: int,
    report: ThematicValidationReport,
    *,
    min_words_per_puzzle: int,
    max_fact_chars_warning: int,
    check_background_files: bool,
    warned_backgrounds: set[str],
) -> None:
    if not spec.title or not spec.title.strip():
        report.add_error("Falta el título del puzzle.", spec)

    if not spec.fact or not spec.fact.strip():
        report.add_error("Falta el fun fact del puzzle.", spec)
    elif len(spec.fact.strip()) > max_fact_chars_warning:
        report.add_warning(
            f"El fun fact tiene {len(spec.fact.strip())} caracteres; puede recortarse visualmente en el layout.",
            spec,
        )

    if not spec.words:
        report.add_error("No hay palabras definidas.", spec)
        return

    normalized_seen: dict[str, str] = {}
    valid_normalized_count = 0

    for original in spec.words:
        normalized = normalize_word_for_grid(original)

        if not normalized:
            report.add_error(
                f"La palabra '{original}' queda vacía tras normalizarla para el grid.",
                spec,
            )
            continue

        valid_normalized_count += 1

        if len(normalized) > grid_size:
            report.add_error(
                f"La palabra '{original}' se normaliza como '{normalized}' y mide {len(normalized)} letras; "
                f"no cabe en un grid de tamaño {grid_size}.",
                spec,
            )

        if normalized in normalized_seen and normalized_seen[normalized] != original:
            report.add_warning(
                f"'{normalized_seen[normalized]}' y '{original}' se normalizan igual: '{normalized}'.",
                spec,
            )
        else:
            normalized_seen[normalized] = original

    if valid_normalized_count < min_words_per_puzzle:
        report.add_error(
            f"Solo hay {valid_normalized_count} palabra(s) válida(s) tras normalizar; "
            f"el mínimo requerido es {min_words_per_puzzle}.",
            spec,
        )

    if check_background_files and spec.block_background:
        _validate_background_once(spec, report, warned_backgrounds)


def _validate_background_once(
    spec: PuzzleSpec,
    report: ThematicValidationReport,
    warned_backgrounds: set[str],
) -> None:
    background = spec.block_background
    if not background or os.path.exists(background):
        return

    if background in warned_backgrounds:
        return

    warned_backgrounds.add(background)

    block_name = spec.block_name or "Bloque sin nombre"
    report.add_warning(
        f"No se encuentra el fondo '{background}'. Se usará fondo blanco/default.",
        context=f"Bloque '{block_name}'",
    )
