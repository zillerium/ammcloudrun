from typing import List
from .constants import Constants

class MathUtils:
    def exp(self, x: int) -> int:
        """Calculate e^x with 1e18 precision."""
        if x <= -41446531673892822313:
            return 0
        assert x < 135305999368893231589, "wad_exp overflow"
        value = (x << 78) // (5 ** 18)
        k = ((value << 96) // 54916777467707473351141471128 + 2**95) >> 96
        value = value - k * 54916777467707473351141471128
        y = ((value + 1346386616545796478920950773328) * value) >> 96
        y = y + 57155421227552351082224309758442
        p = ((y + value - 94201549194550492254356042504812) * y) >> 96
        p = p * 28719021644029726153956944680412240 + value
        p = p + (4385272521454847904659076985693276 << 96)
        q = ((value - 2855989394907223263936484059900) * value) >> 96
        q = q * value - 533845033583426703283633433725380
        q = (q * value >> 96) + 3604857256930695427073651918091429
        q = (q * value >> 96) - 14423608567350463180887372962807573
        q = (q * value >> 96) + 26449188498355588339934803723976023
        r = p // q
        return (r * 3822833074963236453042738258902158003155416615667) >> (195 - k)

    def get_D(self, xp: List[int], amp: int) -> int:
        """Calculate D invariant iteratively."""
        S = sum(xp)
        if S == 0:
            return 0
        D = S
        Ann = amp * Constants.MAX_COINS
        for _ in range(255):
            D_P = D
            for x in xp:
                D_P = (D_P * D) // x
            D_P //= Constants.MAX_COINS ** Constants.MAX_COINS
            Dprev = D
            D = ((Ann * S // Constants.A_PRECISION + D_P * Constants.MAX_COINS) * D) // (
                ((Ann - Constants.A_PRECISION) * D // Constants.A_PRECISION) + (Constants.MAX_COINS + 1) * D_P
            )
            if abs(D - Dprev) <= 1:
                return D
        raise ValueError("D did not converge")

    def get_y(self, i: int, j: int, x: int, xp: List[int], amp: int, D: int) -> int:
        """Calculate x[j] given x[i] = x."""
        assert i != j and 0 <= j < Constants.MAX_COINS and 0 <= i < Constants.MAX_COINS
        S_ = 0
        c = D
        Ann = amp * Constants.MAX_COINS
        for _i in range(Constants.MAX_COINS):
            if _i >= len(xp):
                break
            if _i == i:
                _x = x
            elif _i != j:
                _x = xp[_i]
            else:
                continue
            S_ += _x
            c = (c * D) // (_x * Constants.MAX_COINS)
        c = (c * D * Constants.A_PRECISION) // (Ann * Constants.MAX_COINS)
        b = S_ + (D * Constants.A_PRECISION) // Ann
        y = D
        for _ in range(255):
            y_prev = y
            y = (y * y + c) // (2 * y + b - D)
            if abs(y - y_prev) <= 1:
                return y
        raise ValueError("y did not converge")
