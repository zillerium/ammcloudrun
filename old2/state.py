class AMMState:
    """
    Base class: holds pool state (x, y, A, D).
    Delegates invariant calculations to subclasses.
    """
    def __init__(self, balance_x: float, balance_y: float, A: int = 100):
        self.x = float(balance_x)
        self.y = float(balance_y)
        self.A = A
        self.D = None  # computed later

    def refresh_D(self):
        """Ask CalcD to compute invariant from current x, y."""
        self.D = self._calculate_D(self.x, self.y)
        return self.D

    def solve_y(self, x_new: float) -> float:
        """Ask CalcY to compute y given x_new and current D."""
        if self.D is None:
            self.refresh_D()
        return self._calculate_y(x_new, self.D)

