# classcode/checkstates.py
class CheckStates:
    """
    Validates (x, y) points against StableSwap invariant (n=2).
    """
    def __init__(self, A: int, D: float):
        self.A = A
        self.D = D

    def delta(self, x: float, y: float) -> float:
        lhs = 4 * self.A * (x + y) + self.D
        rhs = 4 * self.A * self.D + self.D**3 / (4 * x * y)
        return lhs - rhs

