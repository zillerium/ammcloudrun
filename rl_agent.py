from collections import deque

class GridWorld:
    """
    Represents the environment.
    The agent lives in a 2D grid, with some squares marked as 'danger zones' that it must avoid.
    The goal is always the bottom-right corner (rows-1, cols-1).
    """

    def __init__(self, rows, cols, danger_zones):
        self.rows = rows                      # Number of rows in the grid
        self.cols = cols                      # Number of columns in the grid
        self.danger_zones = set(tuple(dz) for dz in danger_zones)  # Set of blocked positions
        # self.goal = (rows - 1, cols - 1)      # Goal is the bottom-right corner
        self.goal_col = cols - 1

    def is_valid(self, pos):
        """
        Checks whether the given position is within bounds and not a danger zone.
        Used to filter out invalid or blocked moves.
        """
        r, c = pos
        return (
            0 <= r < self.rows and
            0 <= c < self.cols and
            pos not in self.danger_zones
        )

    def get_neighbors(self, pos):
        """
        Returns a list of valid neighboring positions (up, down, left, right) that the agent can move to.
        """
        r, c = pos
        moves = [(0,1), (1,0), (0,-1), (-1,0)]  # right, down, left, up
        return [(r+dr, c+dc) for dr, dc in moves if self.is_valid((r+dr, c+dc))]


class Agent:
    """
    The Agent.
    This version is a rule-based (non-learning) agent that uses BFS to find a path.
    Future versions may use Q-learning or policy networks.
    """

    def __init__(self, env: GridWorld):
        self.env = env            # Reference to the environment
        self.start = (0, 0)       # Always start at top-left

    def act(self):
        """
        Uses Breadth-First Search (BFS) to find the shortest path from start to goal.
        BFS is optimal for unweighted grids but not suitable for learning or dynamic environments.
        """
        # Each item in queue: (current_position, path_taken)
        queue = deque([(self.start, [self.start])])
        visited = set([self.start])  # Tracks where we've already been

        while queue:
            current, path = queue.popleft()

            # Goal check
            if current[1] == self.env.goal_col:
                return path

            # Explore neighbors
            for neighbor in self.env.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []  # No path found

