"""
Grid management for the AI Pathfinder Visualizer.
Handles grid creation, resetting, clearing search state, and loading preset mazes.
"""

import random

from .constants import CellType, CellState


def create_grid(rows, cols):
    """Create an empty grid of the given dimensions."""
    return [[CellType.EMPTY for _ in range(cols)] for _ in range(rows)]


def create_cell_states(rows, cols):
    """Create an empty cell-state grid."""
    return [[CellState.NONE for _ in range(cols)] for _ in range(rows)]


def reset_grid(app):
    """Reset the entire grid and search state."""
    if not app.searching:
        app.grid = create_grid(app.rows, app.cols)
        app.cell_states = create_cell_states(app.rows, app.cols)
        app.start = None
        app.target = None
        clear_search(app)
        app.mode = 'wall'
        app.update_status("Grid reset!", app.Colors.UI_TEXT)


def clear_search(app):
    """Clear only the search state (keep walls/start/target)."""
    app.frontier = None
    app.explored = set()
    app.came_from = {}
    app.final_path = []
    app.search_complete = False
    app.searching = False
    app.step_count = 0
    app.cost_so_far = {}
    app.current_depth_limit = 0

    # Bidirectional
    app.frontier_forward = None
    app.frontier_backward = None
    app.explored_forward = set()
    app.explored_backward = set()
    app.came_from_forward = {}
    app.came_from_backward = {}
    app.meeting_point = None


def clear_search_visual(app):
    """Clear search state and visual cell states."""
    if not app.searching:
        clear_search(app)
        app.cell_states = create_cell_states(app.rows, app.cols)
        app.update_status("Search cleared!", app.Colors.WARNING)


def load_preset(app, preset_name):
    """Load a preset maze configuration."""
    if app.searching:
        return

    reset_grid(app)

    if preset_name == 'simple':
        app.start = (5, 5)
        app.target = (app.rows - 6, app.cols - 6)

    elif preset_name == 'maze':
        app.start = (2, 2)
        app.target = (app.rows - 3, app.cols - 3)
        for i in range(5, app.rows - 5, 8):
            for j in range(5, app.cols - 5):
                app.grid[i][j] = CellType.WALL
            for j in range(10, app.cols - 5):
                if i + 4 < app.rows:
                    app.grid[i + 4][j] = CellType.WALL
            app.grid[i][app.cols - 10] = CellType.EMPTY
            if i + 4 < app.rows:
                app.grid[i + 4][10] = CellType.EMPTY

    elif preset_name == 'spiral':
        app.start = (app.rows // 2, app.cols // 2)
        app.target = (2, 2)
        for layer in range(1, min(app.rows, app.cols) // 4):
            offset = layer * 3
            for j in range(offset, app.cols - offset):
                if offset < app.rows:
                    app.grid[offset][j] = CellType.WALL
            for i in range(offset, app.rows - offset):
                if app.cols - offset - 1 >= 0:
                    app.grid[i][app.cols - offset - 1] = CellType.WALL
            for j in range(offset, app.cols - offset):
                if app.rows - offset - 1 >= 0:
                    app.grid[app.rows - offset - 1][j] = CellType.WALL
            for i in range(offset + 1, app.rows - offset):
                if offset >= 0:
                    app.grid[i][offset] = CellType.WALL
            if offset + 3 < app.cols:
                app.grid[offset][offset + 3] = CellType.EMPTY

    elif preset_name == 'random':
        app.start = (5, 5)
        app.target = (app.rows - 6, app.cols - 6)
        for i in range(app.rows):
            for j in range(app.cols):
                if (i, j) != app.start and (i, j) != app.target:
                    if random.random() < 0.25:
                        app.grid[i][j] = CellType.WALL

    if app.start:
        app.grid[app.start[0]][app.start[1]] = CellType.START
    if app.target:
        app.grid[app.target[0]][app.target[1]] = CellType.TARGET

    app.update_status(f"{preset_name.capitalize()} maze loaded!", app.Colors.SUCCESS)
