# 🧠 AI Pathfinder Visualizer

An **interactive Algorithm Visualizer** built with Python & Pygame that brings AI search algorithms to life in a grid-based environment. Watch pathfinding algorithms explore nodes step by step and discover the shortest path from start to target — connecting theory with practical implementation.

> Developed as part of an **Artificial Intelligence** course assignment by **Abdullah**.

---

## 🎯 What It Does

This application provides a visual, real-time simulation of how different AI search algorithms navigate through a grid to find a path between two points. Users can draw walls/obstacles, place start and target nodes, and then watch as the chosen algorithm explores the grid — highlighting frontier nodes, explored nodes, and the final path.

### Algorithms Implemented

| Algorithm | Type | Data Structure | Optimal? | Complete? |
|---|---|---|---|---|
| **Breadth-First Search (BFS)** | Uninformed | Queue (FIFO) | ✅ Yes | ✅ Yes |
| **Depth-First Search (DFS)** | Uninformed | Stack (LIFO) | ❌ No | ❌ No |
| **Uniform-Cost Search (UCS)** | Uninformed | Priority Queue | ✅ Yes | ✅ Yes |
| **Depth-Limited Search (DLS)** | Uninformed | Stack + Depth Limit | ❌ No | ❌ No |
| **Iterative Deepening DFS (IDDFS)** | Uninformed | Stack + Iterating Depth | ✅ Yes | ✅ Yes |
| **Bidirectional Search** | Uninformed | Two Queues | ✅ Yes | ✅ Yes |

---

## ✨ Features

- **🗺️ Interactive Grid System** — Click and drag to draw walls/obstacles on a 30×50 grid
- **🔄 Real-Time Visualization** — Watch algorithms explore nodes live with color-coded states
- **📍 Start & End Node Selection** — Place start (green) and target (red) points anywhere on the grid
- **🎬 Animated Path Exploration** — Frontier (orange), explored (blue), and final path (purple) are clearly distinguished
- **⚡ Adjustable Speed** — Control animation speed to observe algorithms at your own pace
- **🧩 Preset Mazes** — Load built-in presets (Simple, Maze, Spiral, Random) to quickly test algorithms
- **📊 Search Statistics** — View step count, explored nodes, and path length after each search
- **🎹 Keyboard Shortcuts** — Quick access to all features via keyboard (1-6 for algorithms, S/T for start/target, Space to run)

---

## 🎨 Color Legend

| Color | Meaning |
|---|---|
| ⬜ White | Empty cell |
| ⬛ Dark Grey | Wall / Obstacle |
| 🟩 Green | Start node |
| 🟥 Red | Target node |
| 🟧 Orange | Frontier (nodes to be explored) |
| 🟦 Blue | Explored nodes |
| 🟪 Purple | Final path |
| 🫐 Teal | Backward explored (Bidirectional) |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.x**
- **Pygame**

### Installation

```bash
# Clone the repository
git clone https://github.com/shaka912/ai-pathfinder-visualizer.git
cd ai-pathfinder-visualizer

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

---

## 🕹️ Controls

| Action | Control |
|---|---|
| **Draw / Erase Walls** | Left Click + Drag |
| **Erase Wall** | Right Click |
| **Set Start Point** | Press `S`, then click on grid |
| **Set Target Point** | Press `T`, then click on grid |
| **Run Algorithm** | `Space` or click ▶ Run |
| **Select Algorithm** | Click button or press `1`–`6` |
| **Clear Search** | Press `C` |
| **Reset Grid** | Press `R` |
| **Adjust Speed** | ➕ / ➖ buttons |
| **Adjust Depth Limit (DLS)** | D+ / D- buttons |

---

## 📚 How Each Algorithm Works

### 1. Breadth-First Search (BFS)
Explores all neighbors at the current depth before moving deeper. Uses a **FIFO queue**. Guarantees the shortest path in an unweighted grid.

### 2. Depth-First Search (DFS)
Dives as deep as possible along each branch before backtracking. Uses a **LIFO stack**. Fast but does not guarantee the shortest path.

### 3. Uniform-Cost Search (UCS)
Expands the node with the **lowest cumulative cost** using a priority queue. Accounts for diagonal movement cost (`1.414`) vs. straight movement (`1.0`). Always finds the optimal path.

### 4. Depth-Limited Search (DLS)
A variant of DFS that imposes a **maximum depth limit** (adjustable via D+/D-). Prevents infinite exploration but may miss solutions beyond the limit.

### 5. Iterative Deepening DFS (IDDFS)
Repeatedly runs DLS with **increasing depth limits** (0, 1, 2, ...). Combines the space efficiency of DFS with the completeness of BFS.

### 6. Bidirectional Search
Runs **two simultaneous BFS searches** — one from the start and one from the target — until they meet in the middle. Dramatically reduces the search space.

---

## 🛠️ Tech Stack

- **Language:** Python 3
- **Graphics:** Pygame
- **Data Structures:** `deque` (queues), `heapq` (priority queues), lists (stacks), sets
- **Architecture:** Modular package design

### Project Structure

```
├── main.py                  # Entry point
├── pathfinder/
│   ├── __init__.py
│   ├── constants.py         # Enums (CellType, CellState) + Colors
│   ├── algorithms.py        # All 6 search algorithms
│   ├── grid.py              # Grid management + preset mazes
│   ├── ui.py                # Button rendering + grid drawing
│   └── app.py               # Main application (game loop, events)
├── requirements.txt
├── README.md
└── LICENSE
```

---

## 📖 What We Learned

- Search strategies and graph traversal in Artificial Intelligence
- Practical use of data structures like **queues**, **stacks**, and **priority queues**
- Event handling and real-time visualization logic with Pygame
- Writing **modular and readable** Python code
- Collaborative development using **GitHub** with proper commit history

---



## 👥 Contributors

- **Abdullah**

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
