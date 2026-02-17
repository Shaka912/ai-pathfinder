"""
Constants for the AI Pathfinder Visualizer.
Contains cell types, cell states, color palette, and grid defaults.
"""

from enum import Enum


# ─── Grid Defaults ───────────────────────────────────────────────────────────

DEFAULT_ROWS = 30
DEFAULT_COLS = 50
DEFAULT_CELL_SIZE = 16


# ─── Enums ───────────────────────────────────────────────────────────────────

class CellType(Enum):
    EMPTY = 0
    WALL = 1
    START = 2
    TARGET = 3


class CellState(Enum):
    NONE = 0
    FRONTIER = 1
    EXPLORED = 2
    PATH = 3
    FRONTIER2 = 4      # Bidirectional search (second frontier)
    EXPLORED2 = 5      # Bidirectional search (second explored)


# ─── Color Palette ───────────────────────────────────────────────────────────

class Colors:
    """Color palette for the visualizer."""

    # Cell colors
    EMPTY = (255, 255, 255)
    WALL = (44, 62, 80)
    START = (39, 174, 96)
    TARGET = (231, 76, 60)

    # Search state colors
    FRONTIER = (243, 156, 18)
    EXPLORED = (52, 152, 219)
    PATH = (155, 89, 182)
    FRONTIER2 = (230, 126, 34)          # Orange for second frontier
    EXPLORED2 = (26, 188, 156)          # Teal for second explored

    # UI colors
    GRID_LINE = (189, 195, 199)
    BG = (236, 240, 241)
    UI_BG = (52, 73, 94)
    UI_TEXT = (236, 240, 241)
    BUTTON = (46, 204, 113)
    BUTTON_HOVER = (39, 174, 96)
    BUTTON_SELECTED = (241, 196, 15)

    # Status colors
    WARNING = (230, 126, 34)
    SUCCESS = (46, 204, 113)
    ERROR = (231, 76, 60)
