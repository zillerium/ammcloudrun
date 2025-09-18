# classcode/dstate.py
import math

class DState:
    """
    Represents the invariant state of the AMM: x, y, A, D.
    D is computed from x, y, A at initialization.
    """
    def __init__(self, xb: float, yb: float, A: int):
        self.x = float(xb)
        self.y = float(yb)
        self.A = int(A)
        self.D = self._calculate_D(xb, yb)

    def _calculate_D(self, x: float, y: float) -> float:
        """Newton iteration for n=2 case."""
        S = x + y
        if S == 0:
            return 0

        D = S
        Ann = self.A * 4

        for _ in range(255):
            D_P = D * D * D / (4 * x * y)
            D_prev = D
            numerator = (Ann * S + D_P * 2) * D
            denominator = (Ann - 1) * D + D_P * 3
            D = numerator / denominator
            if abs(D - D_prev) <= 1:
                break
        return D

