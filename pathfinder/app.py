"""
Main application class for the AI Pathfinder Visualizer.
Orchestrates grid, algorithms, UI, and the game loop.
"""

import sys
from collections import deque
import heapq

import pygame

from .constants import (
    CellType, CellState, Colors,
    DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_CELL_SIZE,
)
from .algorithms import algorithm_step
from .grid import (
    create_grid, create_cell_states,
    reset_grid, clear_search, clear_search_visual, load_preset,
)
from .ui import create_button, draw_ui_panel, draw_grid


class PathfinderApp:
    """Complete pathfinder application with all 6 algorithms."""

    # Expose Colors on the instance so grid/ui helpers can access via app.Colors
    Colors = Colors

    def __init__(self, rows=DEFAULT_ROWS, cols=DEFAULT_COLS, cell_size=DEFAULT_CELL_SIZE):
        pygame.init()

        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        self.grid_width = cols * cell_size
        self.grid_height = rows * cell_size
        self.ui_height = 220
        self.window_width = self.grid_width
        self.window_height = self.grid_height + self.ui_height

        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("🎮 AI Pathfinder - All 6 Algorithms")

        # Fonts
        self.title_font = pygame.font.Font(None, 28)
        self.button_font = pygame.font.Font(None, 18)
        self.info_font = pygame.font.Font(None, 16)
        self.stats_font = pygame.font.Font(None, 15)

        # Grid
        self.grid = create_grid(rows, cols)
        self.cell_states = create_cell_states(rows, cols)

        # State
        self.start = None
        self.target = None
        self.mode = 'wall'
        self.dragging = False
        self.drag_erase = False

        # Algorithm selection
        self.selected_algorithm = 'BFS'
        self.algorithms = ['BFS', 'DFS', 'UCS', 'DLS', 'IDDFS', 'Bidirectional']

        # Search state
        self.frontier = None
        self.explored = set()
        self.came_from = {}
        self.final_path = []
        self.search_complete = False
        self.searching = False
        self.step_count = 0

        # Algorithm-specific state
        self.depth_limit = 20       # For DLS
        self.current_depth_limit = 0  # For IDDFS
        self.cost_so_far = {}       # For UCS

        # Bidirectional specific
        self.frontier_forward = None
        self.frontier_backward = None
        self.explored_forward = set()
        self.explored_backward = set()
        self.came_from_forward = {}
        self.came_from_backward = {}
        self.meeting_point = None

        # Animation
        self.animation_delay = 20
        self.last_step_time = 0
        self.clock = pygame.time.Clock()
        self.fps = 60

        self.status_message = "Select an algorithm and create a maze!"
        self.status_color = Colors.UI_TEXT

        self.setup_buttons()

    # ─── Buttons ─────────────────────────────────────────────────────────

    def setup_buttons(self):
        """Setup all UI buttons."""
        bw, bh = 75, 28
        spacing = 6
        start_x = 10

        # Row 1: Algorithm selection
        y1 = 12
        self.algo_buttons = []
        for i, algo in enumerate(self.algorithms):
            btn = create_button(
                start_x + (bw + spacing) * i, y1, bw, bh,
                algo, lambda a=algo: self.select_algorithm(a),
                Colors.BUTTON_SELECTED if algo == self.selected_algorithm else Colors.BUTTON,
            )
            self.algo_buttons.append(btn)

        # Row 2: Main controls
        y2 = 50
        self.control_buttons = [
            create_button(start_x, y2, bw, bh, "Start (S)", self.set_start_mode),
            create_button(start_x + (bw + spacing) * 1, y2, bw, bh, "Target (T)", self.set_target_mode),
            create_button(start_x + (bw + spacing) * 2, y2, bw, bh, "▶ Run", self.start_search, Colors.SUCCESS),
            create_button(start_x + (bw + spacing) * 3, y2, bw, bh, "Clear", lambda: clear_search_visual(self), Colors.WARNING),
            create_button(start_x + (bw + spacing) * 4, y2, bw, bh, "Reset", lambda: reset_grid(self), Colors.ERROR),
        ]

        # Row 3: Presets
        y3 = 88
        self.preset_buttons = [
            create_button(start_x, y3, bw, bh, "Simple", lambda: load_preset(self, 'simple')),
            create_button(start_x + (bw + spacing) * 1, y3, bw, bh, "Maze", lambda: load_preset(self, 'maze')),
            create_button(start_x + (bw + spacing) * 2, y3, bw, bh, "Spiral", lambda: load_preset(self, 'spiral')),
            create_button(start_x + (bw + spacing) * 3, y3, bw, bh, "Random", lambda: load_preset(self, 'random')),
        ]

        # Speed and depth controls
        speed_x = self.window_width - 160
        self.misc_buttons = [
            create_button(speed_x, y1, 35, bh, "➖", self.decrease_speed),
            create_button(speed_x + 40, y1, 35, bh, "➕", self.increase_speed),
            create_button(speed_x, y2, 35, bh, "D-", self.decrease_depth),
            create_button(speed_x + 40, y2, 35, bh, "D+", self.increase_depth),
        ]

        self.all_buttons = (
            self.algo_buttons + self.control_buttons +
            self.preset_buttons + self.misc_buttons
        )

    # ─── Actions ─────────────────────────────────────────────────────────

    def select_algorithm(self, algo):
        """Select which algorithm to use."""
        if not self.searching:
            self.selected_algorithm = algo
            for btn in self.algo_buttons:
                btn['color'] = Colors.BUTTON_SELECTED if btn['text'] == algo else btn['base_color']
            self.update_status(f"{algo} selected! Press ▶ Run or SPACE to start", Colors.SUCCESS)

    def set_start_mode(self):
        if not self.searching:
            self.mode = 'start'
            self.update_status("Click anywhere to place START point", Colors.SUCCESS)

    def set_target_mode(self):
        if not self.searching:
            self.mode = 'target'
            self.update_status("Click anywhere to place TARGET point", Colors.ERROR)

    def increase_speed(self):
        self.animation_delay = max(1, self.animation_delay - 10)
        self.update_status(f"Speed: {self.animation_delay}ms delay", Colors.UI_TEXT)

    def decrease_speed(self):
        self.animation_delay = min(200, self.animation_delay + 10)
        self.update_status(f"Speed: {self.animation_delay}ms delay", Colors.UI_TEXT)

    def increase_depth(self):
        self.depth_limit = min(100, self.depth_limit + 5)
        self.update_status(f"DLS Depth Limit: {self.depth_limit}", Colors.UI_TEXT)

    def decrease_depth(self):
        self.depth_limit = max(5, self.depth_limit - 5)
        self.update_status(f"DLS Depth Limit: {self.depth_limit}", Colors.UI_TEXT)

    def update_status(self, message, color=None):
        self.status_message = message
        if color:
            self.status_color = color

    # ─── Search ──────────────────────────────────────────────────────────

    def start_search(self):
        """Initialize search based on the selected algorithm."""
        if self.searching:
            return
        if not self.start or not self.target:
            self.update_status("ERROR: Set Start and Target first!", Colors.ERROR)
            return

        clear_search(self)
        self.cell_states = create_cell_states(self.rows, self.cols)
        self.searching = True

        algo = self.selected_algorithm

        if algo == 'BFS':
            self.frontier = deque([self.start])
            self.came_from = {self.start: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER

        elif algo == 'DFS':
            self.frontier = [self.start]  # Stack
            self.came_from = {self.start: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER

        elif algo == 'UCS':
            self.frontier = [(0, self.start)]  # Priority queue
            heapq.heapify(self.frontier)
            self.came_from = {self.start: None}
            self.cost_so_far = {self.start: 0}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER

        elif algo == 'DLS':
            self.frontier = [(self.start, 0)]  # Stack with depth
            self.came_from = {self.start: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER

        elif algo == 'IDDFS':
            self.current_depth_limit = 0
            self.frontier = [(self.start, 0)]
            self.came_from = {self.start: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER

        elif algo == 'Bidirectional':
            self.frontier_forward = deque([self.start])
            self.frontier_backward = deque([self.target])
            self.came_from_forward = {self.start: None}
            self.came_from_backward = {self.target: None}
            self.cell_states[self.start[0]][self.start[1]] = CellState.FRONTIER
            self.cell_states[self.target[0]][self.target[1]] = CellState.FRONTIER2

        self.update_status(f"🔍 {algo} searching...", Colors.WARNING)

    def finish_search(self, found):
        """Complete the search and display results."""
        self.search_complete = True
        self.searching = False

        if found:
            msg = f"✓ PATH FOUND! | {self.selected_algorithm} | "
            msg += f"Steps: {self.step_count} | "

            if self.selected_algorithm == 'Bidirectional':
                explored = len(self.explored_forward) + len(self.explored_backward)
            else:
                explored = len(self.explored)

            msg += f"Explored: {explored} | Path: {len(self.final_path)}"

            if self.selected_algorithm == 'IDDFS':
                msg += f" | Depth: {self.current_depth_limit}"

            self.update_status(msg, Colors.SUCCESS)
        else:
            msg = f"❌ NO PATH | {self.selected_algorithm} | Steps: {self.step_count}"
            if self.selected_algorithm == 'DLS':
                msg += f" | Depth limit: {self.depth_limit}"
            elif self.selected_algorithm == 'IDDFS':
                msg += f" | Max depth reached: {self.current_depth_limit}"
            self.update_status(msg, Colors.ERROR)

    # ─── Events ──────────────────────────────────────────────────────────

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            for button in self.all_buttons:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if button['rect'].collidepoint(event.pos) and button['enabled']:
                        button['callback']()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_s:
                    self.set_start_mode()
                elif event.key == pygame.K_t:
                    self.set_target_mode()
                elif event.key == pygame.K_SPACE:
                    self.start_search()
                elif event.key == pygame.K_c:
                    clear_search_visual(self)
                elif event.key == pygame.K_r:
                    reset_grid(self)
                elif event.key == pygame.K_1:
                    self.select_algorithm('BFS')
                elif event.key == pygame.K_2:
                    self.select_algorithm('DFS')
                elif event.key == pygame.K_3:
                    self.select_algorithm('UCS')
                elif event.key == pygame.K_4:
                    self.select_algorithm('DLS')
                elif event.key == pygame.K_5:
                    self.select_algorithm('IDDFS')
                elif event.key == pygame.K_6:
                    self.select_algorithm('Bidirectional')

            if event.type == pygame.MOUSEBUTTONDOWN and not self.searching:
                grid_pos = self._get_grid_pos(event.pos)
                if grid_pos:
                    row, col = grid_pos
                    if event.button == 1:
                        self.dragging = True
                        self._handle_grid_click(row, col)
                    elif event.button == 3:
                        if self.grid[row][col] == CellType.WALL:
                            self.grid[row][col] = CellType.EMPTY

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False

            elif event.type == pygame.MOUSEMOTION and self.dragging and not self.searching:
                grid_pos = self._get_grid_pos(event.pos)
                if grid_pos and self.mode == 'wall':
                    row, col = grid_pos
                    if (row, col) != self.start and (row, col) != self.target:
                        if self.drag_erase:
                            self.grid[row][col] = CellType.EMPTY
                        else:
                            self.grid[row][col] = CellType.WALL

        return True

    def _get_grid_pos(self, mouse_pos):
        """Convert mouse position to grid coordinates."""
        x, y = mouse_pos
        y -= self.ui_height
        if y < 0 or y >= self.grid_height:
            return None
        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col)
        return None

    def _handle_grid_click(self, row, col):
        """Handle a click on a grid cell."""
        if self.mode == 'wall':
            if (row, col) != self.start and (row, col) != self.target:
                if self.grid[row][col] == CellType.WALL:
                    self.grid[row][col] = CellType.EMPTY
                    self.drag_erase = True
                else:
                    self.grid[row][col] = CellType.WALL
                    self.drag_erase = False

        elif self.mode == 'start':
            if self.start:
                old_row, old_col = self.start
                self.grid[old_row][old_col] = CellType.EMPTY
            self.start = (row, col)
            self.grid[row][col] = CellType.START
            self.mode = 'wall'
            self.update_status("Start set! Now set Target (T)", Colors.SUCCESS)

        elif self.mode == 'target':
            if self.target:
                old_row, old_col = self.target
                self.grid[old_row][old_col] = CellType.EMPTY
            self.target = (row, col)
            self.grid[row][col] = CellType.TARGET
            self.mode = 'wall'
            self.update_status("Target set! Press ▶ Run", Colors.SUCCESS)

    # ─── Game Loop ───────────────────────────────────────────────────────

    def update(self):
        """Update game state — step the algorithm if searching."""
        if self.searching:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_step_time >= self.animation_delay:
                algorithm_step(self)
                self.last_step_time = current_time

    def draw(self):
        """Draw everything to the screen."""
        self.screen.fill(Colors.BG)
        draw_ui_panel(self.screen, self)
        draw_grid(self.screen, self)
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        print("\n" + "=" * 70)
        print("🎮 AI PATHFINDER - ALL 6 ALGORITHMS")
        print("=" * 70)
        print("\nAlgorithms Available:")
        print("  1. BFS - Breadth-First Search")
        print("  2. DFS - Depth-First Search")
        print("  3. UCS - Uniform-Cost Search")
        print("  4. DLS - Depth-Limited Search")
        print("  5. IDDFS - Iterative Deepening DFS")
        print("  6. Bidirectional Search")
        print("\nPress 1-6 to select algorithm or click buttons!")
        print("=" * 70)
        print("\nGame window opened! Compare different search strategies!\n")

        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

        pygame.quit()
        sys.exit()
