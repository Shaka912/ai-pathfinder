"""
AI Pathfinder Visualizer — Entry Point
=======================================
Run this file to launch the interactive pathfinding visualizer.

    python main.py

See README.md for controls and documentation.
"""

from pathfinder.app import PathfinderApp


def main():
    game = PathfinderApp(rows=30, cols=50, cell_size=16)
    game.run()


if __name__ == "__main__":
    main()
