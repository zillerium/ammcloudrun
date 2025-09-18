from .state import AMMState

class CalcD(AMMState):
    """
    Subclass responsible for computing invariant D.
    """
    def _calculate_D(self, x: float, y: float) -> float:
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

