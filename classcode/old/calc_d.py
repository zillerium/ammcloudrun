import math
from .state import AMMState

class CalcD(AMMState):
    """
    Subclass to calculate the invariant D.
    """

    def _calculate_D(self, x: float = None, y: float = None) -> float:
        """Newton-Raphson iteration"""
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        S = x + y
        if S == 0:
            return 0

        D = S  # initial guess
        Ann = self.A * 4  # A * n^n (n=2 → 4)

        for _ in range(255):
            D_P = D * D * D / (4 * x * y)
            D_prev = D
            numerator = (Ann * S + D_P * 2) * D
            denominator = (Ann - 1) * D + D_P * 3
            D = numerator / denominator
            if abs(D - D_prev) <= 1:
                break

        return D

    def _calculate_D_2(self, x: float = None, y: float = None) -> float:
        """Closed-form cubic solution (Cardano) for n=2"""
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        xy = x * y
        p = 4 * xy * (4 * self.A - 1)
        q = -16 * self.A * xy * (x + y)

        discriminant = (q / 2) ** 2 + (p / 3) ** 3

        if discriminant >= 0:
            sqrt_disc = math.sqrt(discriminant)
            u_term = -q / 2 + sqrt_disc
            v_term = -q / 2 - sqrt_disc
            u = u_term**(1/3) if u_term >= 0 else -(-u_term) ** (1/3)
            v = v_term**(1/3) if v_term >= 0 else -(-v_term) ** (1/3)
            root = u + v
        else:
            r = math.sqrt(-(p / 3) ** 3)
            phi = math.acos(-q / (2 * r))
            root = 2 * math.sqrt(-p / 3) * math.cos(phi / 3)

        return root

