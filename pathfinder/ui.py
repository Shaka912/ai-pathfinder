"""
UI rendering for the AI Pathfinder Visualizer.
Handles buttons, the control panel, grid drawing, and color mapping.
"""

import pygame

from .constants import CellType, CellState, Colors


# ─── Button Helpers ──────────────────────────────────────────────────────────

def create_button(x, y, w, h, text, callback, color=Colors.BUTTON):
    """Create a button dictionary."""
    return {
        'rect': pygame.Rect(x, y, w, h),
        'text': text,
        'color': color,
        'callback': callback,
        'enabled': True,
        'base_color': color,
    }


def draw_button(screen, button, button_font):
    """Render a single button to the screen."""
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = button['rect'].collidepoint(mouse_pos) and button['enabled']
    color = Colors.BUTTON_HOVER if is_hovered else button['color']

    pygame.draw.rect(screen, color, button['rect'], border_radius=4)
    pygame.draw.rect(screen, Colors.UI_BG, button['rect'], 2, border_radius=4)

    text_surface = button_font.render(button['text'], True, Colors.UI_TEXT)
    text_rect = text_surface.get_rect(center=button['rect'].center)
    screen.blit(text_surface, text_rect)


# ─── Color Mapping ───────────────────────────────────────────────────────────

def get_cell_color(grid, cell_states, row, col):
    """Determine the display color for a cell."""
    cell_type = grid[row][col]
    cell_state = cell_states[row][col]

    if cell_type == CellType.START:
        return Colors.START
    elif cell_type == CellType.TARGET:
        return Colors.TARGET
    elif cell_state == CellState.PATH:
        return Colors.PATH
    elif cell_state == CellState.FRONTIER:
        return Colors.FRONTIER
    elif cell_state == CellState.FRONTIER2:
        return Colors.FRONTIER2
    elif cell_state == CellState.EXPLORED:
        return Colors.EXPLORED
    elif cell_state == CellState.EXPLORED2:
        return Colors.EXPLORED2
    elif cell_type == CellType.WALL:
        return Colors.WALL
    return Colors.EMPTY


# ─── Drawing Functions ───────────────────────────────────────────────────────

def draw_ui_panel(screen, app):
    """Draw the top UI panel with labels, stats, and instructions."""
    # UI background
    ui_rect = pygame.Rect(0, 0, app.window_width, app.ui_height)
    pygame.draw.rect(screen, Colors.UI_BG, ui_rect)

    # Draw all buttons
    for button in app.all_buttons:
        draw_button(screen, button, app.button_font)

    # Section labels
    label1 = app.info_font.render("Select Algorithm (or press 1-6):", True, Colors.UI_TEXT)
    screen.blit(label1, (10, 0))

    label2 = app.info_font.render("Controls:", True, Colors.UI_TEXT)
    screen.blit(label2, (10, 38))

    label3 = app.info_font.render("Presets:", True, Colors.UI_TEXT)
    screen.blit(label3, (10, 76))

    speed_label = app.info_font.render("Speed:", True, Colors.UI_TEXT)
    screen.blit(speed_label, (app.window_width - 160, 0))

    depth_label = app.info_font.render(f"DLS={app.depth_limit}:", True, Colors.UI_TEXT)
    screen.blit(depth_label, (app.window_width - 160, 38))

    # Status message
    status_surface = app.info_font.render(app.status_message, True, app.status_color)
    screen.blit(status_surface, (10, 125))

    # Stats
    if app.selected_algorithm == 'Bidirectional':
        explored = len(app.explored_forward) + len(app.explored_backward)
        frontier = len(app.frontier_forward) if app.frontier_forward else 0
        frontier += len(app.frontier_backward) if app.frontier_backward else 0
    else:
        explored = len(app.explored)
        frontier = len(app.frontier) if app.frontier else 0

    stats = f"Algorithm: {app.selected_algorithm} | Steps: {app.step_count} | "
    stats += f"Frontier: {frontier} | Explored: {explored} | Path: {len(app.final_path)}"

    if app.selected_algorithm == 'IDDFS':
        stats += f" | Current Depth: {app.current_depth_limit}"

    stats_surface = app.stats_font.render(stats, True, Colors.WARNING)
    screen.blit(stats_surface, (10, 145))

    # Instructions
    instructions = "S=Start | T=Target | SPACE=Run | C=Clear | R=Reset | Drag=Walls | ESC=Exit"
    inst_surface = app.stats_font.render(instructions, True, Colors.UI_TEXT)
    screen.blit(inst_surface, (10, 165))

    # Algorithm info
    algo_info = {
        'BFS': "BFS: Queue (FIFO) - Guarantees shortest path",
        'DFS': "DFS: Stack (LIFO) - Goes deep first",
        'UCS': "UCS: Priority Queue - Considers edge costs",
        'DLS': "DLS: Depth-Limited DFS - Stops at depth limit",
        'IDDFS': "IDDFS: Iterative Deepening - Increases depth gradually",
        'Bidirectional': "Bidirectional: Searches from both ends",
    }
    info_text = algo_info[app.selected_algorithm]
    info_surface = app.stats_font.render(info_text, True, Colors.UI_TEXT)
    screen.blit(info_surface, (10, 185))

    algo_delay = f"Delay: {app.animation_delay}ms"
    delay_surface = app.stats_font.render(algo_delay, True, Colors.UI_TEXT)
    screen.blit(delay_surface, (10, 203))


def draw_grid(screen, app):
    """Draw the grid cells and start/target labels."""
    for row in range(app.rows):
        for col in range(app.cols):
            x = col * app.cell_size
            y = row * app.cell_size + app.ui_height
            color = get_cell_color(app.grid, app.cell_states, row, col)
            cell_rect = pygame.Rect(x, y, app.cell_size, app.cell_size)
            pygame.draw.rect(screen, color, cell_rect)
            pygame.draw.rect(screen, Colors.GRID_LINE, cell_rect, 1)

    # Start / Target labels
    label_font = pygame.font.Font(None, int(app.cell_size * 1.3))
    if app.start:
        s_text = label_font.render('S', True, (255, 255, 255))
        s_rect = s_text.get_rect(center=(
            app.start[1] * app.cell_size + app.cell_size // 2,
            app.start[0] * app.cell_size + app.cell_size // 2 + app.ui_height,
        ))
        screen.blit(s_text, s_rect)

    if app.target:
        t_text = label_font.render('T', True, (255, 255, 255))
        t_rect = t_text.get_rect(center=(
            app.target[1] * app.cell_size + app.cell_size // 2,
            app.target[0] * app.cell_size + app.cell_size // 2 + app.ui_height,
        ))
        screen.blit(t_text, t_rect)
