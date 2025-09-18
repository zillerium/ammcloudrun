class StableSwapD:
    """
    Encapsulates calculation of the StableSwap invariant D
    given balances x, y and amplification parameter A.
    """

    @staticmethod
    def calculate_D(x: float, y: float, A: int) -> float:
        """
        Calculate invariant D using Newton-Raphson iteration.
        """
        S = x + y
        if S == 0:
            return 0

        D = S
        Ann = A * 4  # A * n^n where n=2 → n^n = 4

        for _ in range(255):
            D_prev = D
            D_P = D * D * D / (4 * x * y)
            numerator = (Ann * S + D_P * 2) * D
            denominator = (Ann - 1) * D + D_P * 3
            D = numerator / denominator

            if abs(D - D_prev) <= 1:
                break

        return D

