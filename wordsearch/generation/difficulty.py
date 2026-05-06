"""Difficulty levels and generation rules."""

from __future__ import annotations

from enum import Enum


class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


difficulty_settings = {
    DifficultyLevel.EASY: {
        "name": "Fácil",
        "grid_min": 8,
        "grid_max": 12,
        "grid_default": 10,
        "directions": [(0, 1), (1, 0)],
        "allow_reversed": False,
    },
    DifficultyLevel.MEDIUM: {
        "name": "Medio",
        "grid_min": 12,
        "grid_max": 15,
        "grid_default": 14,
        "directions": [(0, 1), (1, 0), (1, 1), (1, -1)],
        "allow_reversed": False,
    },
    DifficultyLevel.HARD: {
        "name": "Difícil",
        "grid_min": 15,
        "grid_max": 20,
        "grid_default": 18,
        "directions": [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ],
        "allow_reversed": True,
    },
}
