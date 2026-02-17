"""
Search algorithms for the AI Pathfinder Visualizer.
Each algorithm step function operates on the shared app state.
"""

import heapq

from .constants import CellType, CellState


def get_neighbors(grid, node, rows, cols):
    """Get valid neighbors of a node (clockwise + some diagonals)."""
    row, col = node
    neighbors = []
    movements = [(-1, 0), (0, 1), (1, 0), (1, 1), (0, -1), (-1, -1)]

    for dr, dc in movements:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < rows and 0 <= new_col < cols:
            if grid[new_row][new_col] != CellType.WALL:
                neighbors.append((new_row, new_col))
    return neighbors


def get_move_cost(from_node, to_node):
    """Calculate cost of move (diagonal = 1.414, straight = 1.0)."""
    r1, c1 = from_node
    r2, c2 = to_node
    if abs(r1 - r2) + abs(c1 - c2) == 2:  # Diagonal
        return 1.414
    return 1.0


# ─── Path Reconstruction ────────────────────────────────────────────────────

def reconstruct_path(app):
    """Reconstruct path from start to target."""
    app.final_path = []
    current = app.target
    while current in app.came_from:
        app.final_path.append(current)
        current = app.came_from[current]
    app.final_path.append(app.start)
    app.final_path.reverse()
    mark_path(app)


def reconstruct_bidirectional_path(app):
    """Reconstruct path for bidirectional search."""
    app.final_path = []

    # Forward path
    current = app.meeting_point
    forward_path = []
    while current in app.came_from_forward:
        forward_path.append(current)
        current = app.came_from_forward[current]
    forward_path.append(app.start)
    forward_path.reverse()

    # Backward path
    current = app.meeting_point
    backward_path = []
    if current in app.came_from_backward and app.came_from_backward[current]:
        current = app.came_from_backward[current]
        while current in app.came_from_backward:
            backward_path.append(current)
            current = app.came_from_backward[current]
        backward_path.append(app.target)

    app.final_path = forward_path + backward_path
    mark_path(app)


def mark_path(app):
    """Mark the final path on the grid."""
    for node in app.final_path:
        if node != app.start and node != app.target:
            app.cell_states[node[0]][node[1]] = CellState.PATH


# ─── Algorithm Steps ─────────────────────────────────────────────────────────

def bfs_step(app):
    """Execute one step of Breadth-First Search."""
    if not app.frontier:
        app.finish_search(False)
        return

    current = app.frontier.popleft()
    app.explored.add(current)
    if current != app.start and current != app.target:
        app.cell_states[current[0]][current[1]] = CellState.EXPLORED

    if current == app.target:
        reconstruct_path(app)
        app.finish_search(True)
        return

    for neighbor in get_neighbors(app.grid, current, app.rows, app.cols):
        if neighbor not in app.explored and neighbor not in app.frontier:
            app.frontier.append(neighbor)
            app.came_from[neighbor] = current
            if neighbor != app.target:
                app.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER

    app.step_count += 1


def dfs_step(app):
    """Execute one step of Depth-First Search."""
    if not app.frontier:
        app.finish_search(False)
        return

    current = app.frontier.pop()  # LIFO - Stack

    if current in app.explored:
        return

    app.explored.add(current)
    if current != app.start and current != app.target:
        app.cell_states[current[0]][current[1]] = CellState.EXPLORED

    if current == app.target:
        reconstruct_path(app)
        app.finish_search(True)
        return

    for neighbor in reversed(get_neighbors(app.grid, current, app.rows, app.cols)):
        if neighbor not in app.explored:
            if neighbor not in [n for n in app.frontier]:
                app.frontier.append(neighbor)
                if neighbor not in app.came_from:
                    app.came_from[neighbor] = current
                if neighbor != app.target:
                    app.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER

    app.step_count += 1


def ucs_step(app):
    """Execute one step of Uniform-Cost Search."""
    if not app.frontier:
        app.finish_search(False)
        return

    cost, current = heapq.heappop(app.frontier)

    if current in app.explored:
        return

    app.explored.add(current)
    if current != app.start and current != app.target:
        app.cell_states[current[0]][current[1]] = CellState.EXPLORED

    if current == app.target:
        reconstruct_path(app)
        app.finish_search(True)
        return

    for neighbor in get_neighbors(app.grid, current, app.rows, app.cols):
        if neighbor not in app.explored:
            new_cost = app.cost_so_far[current] + get_move_cost(current, neighbor)

            if neighbor not in app.cost_so_far or new_cost < app.cost_so_far[neighbor]:
                app.cost_so_far[neighbor] = new_cost
                heapq.heappush(app.frontier, (new_cost, neighbor))
                app.came_from[neighbor] = current
                if neighbor != app.target:
                    app.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER

    app.step_count += 1


def dls_step(app):
    """Execute one step of Depth-Limited Search."""
    if not app.frontier:
        app.finish_search(False)
        return

    current, depth = app.frontier.pop()

    if current in app.explored:
        return

    app.explored.add(current)
    if current != app.start and current != app.target:
        app.cell_states[current[0]][current[1]] = CellState.EXPLORED

    if current == app.target:
        reconstruct_path(app)
        app.finish_search(True)
        return

    if depth < app.depth_limit:
        for neighbor in reversed(get_neighbors(app.grid, current, app.rows, app.cols)):
            if neighbor not in app.explored:
                app.frontier.append((neighbor, depth + 1))
                if neighbor not in app.came_from:
                    app.came_from[neighbor] = current
                if neighbor != app.target:
                    app.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER

    app.step_count += 1


def iddfs_step(app):
    """Execute one step of Iterative Deepening DFS."""
    if not app.frontier:
        # Increase depth limit and restart
        app.current_depth_limit += 1
        if app.current_depth_limit > 50:  # Max depth limit
            app.finish_search(False)
            return

        # Restart search with new depth limit
        app.explored = set()
        app.frontier = [(app.start, 0)]
        app.came_from = {app.start: None}
        app.cell_states = [[CellState.NONE for _ in range(app.cols)] for _ in range(app.rows)]
        app.cell_states[app.start[0]][app.start[1]] = CellState.FRONTIER
        return

    current, depth = app.frontier.pop()

    if current in app.explored:
        return

    app.explored.add(current)
    if current != app.start and current != app.target:
        app.cell_states[current[0]][current[1]] = CellState.EXPLORED

    if current == app.target:
        reconstruct_path(app)
        app.finish_search(True)
        return

    if depth < app.current_depth_limit:
        for neighbor in reversed(get_neighbors(app.grid, current, app.rows, app.cols)):
            if neighbor not in app.explored:
                app.frontier.append((neighbor, depth + 1))
                if neighbor not in app.came_from:
                    app.came_from[neighbor] = current
                if neighbor != app.target:
                    app.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER

    app.step_count += 1


def bidirectional_step(app):
    """Execute one step of Bidirectional Search."""
    if not app.frontier_forward and not app.frontier_backward:
        app.finish_search(False)
        return

    # Alternate between forward and backward
    if app.step_count % 2 == 0 and app.frontier_forward:
        # Forward search
        current = app.frontier_forward.popleft()
        app.explored_forward.add(current)
        if current != app.start:
            app.cell_states[current[0]][current[1]] = CellState.EXPLORED

        # Check if paths meet
        if current in app.explored_backward:
            app.meeting_point = current
            reconstruct_bidirectional_path(app)
            app.finish_search(True)
            return

        for neighbor in get_neighbors(app.grid, current, app.rows, app.cols):
            if neighbor not in app.explored_forward and neighbor not in app.frontier_forward:
                app.frontier_forward.append(neighbor)
                app.came_from_forward[neighbor] = current
                if neighbor != app.target:
                    app.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER

    elif app.frontier_backward:
        # Backward search
        current = app.frontier_backward.popleft()
        app.explored_backward.add(current)
        if current != app.target:
            app.cell_states[current[0]][current[1]] = CellState.EXPLORED2

        # Check if paths meet
        if current in app.explored_forward:
            app.meeting_point = current
            reconstruct_bidirectional_path(app)
            app.finish_search(True)
            return

        for neighbor in get_neighbors(app.grid, current, app.rows, app.cols):
            if neighbor not in app.explored_backward and neighbor not in app.frontier_backward:
                app.frontier_backward.append(neighbor)
                app.came_from_backward[neighbor] = current
                if neighbor != app.start:
                    app.cell_states[neighbor[0]][neighbor[1]] = CellState.FRONTIER2

    app.step_count += 1


def algorithm_step(app):
    """Execute one step of the currently selected algorithm."""
    algo = app.selected_algorithm

    if algo == 'BFS':
        return bfs_step(app)
    elif algo == 'DFS':
        return dfs_step(app)
    elif algo == 'UCS':
        return ucs_step(app)
    elif algo == 'DLS':
        return dls_step(app)
    elif algo == 'IDDFS':
        return iddfs_step(app)
    elif algo == 'Bidirectional':
        return bidirectional_step(app)
