class CalcD:
    def __init__(self, n_coins: int, a_precision: int = 100):
        self.n_coins = n_coins
        self.A_PRECISION = a_precision

    def get_D(self, xp: list[int], amp: int) -> int:
        """
        Compute the Curve invariant D for given balances and amplification.
        """
        S = sum(xp)
        if S == 0:
            return 0

        D = S
        Ann = amp * self.n_coins

        for _ in range(255):
            D_P = D
            for x in xp:
                D_P = D_P * D // x  # integer division
            D_P //= self.n_coins ** self.n_coins
            Dprev = D

            numerator = (Ann * S // self.A_PRECISION + D_P * self.n_coins) * D
            denominator = (Ann - self.A_PRECISION) * D // self.A_PRECISION + (self.n_coins + 1) * D_P
            D = numerator // denominator

            if abs(D - Dprev) <= 1:
                return D

        raise Exception("get_D did not converge")

