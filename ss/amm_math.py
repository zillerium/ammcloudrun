# amm_math.py

# ---- Constants ----
MAX_COINS = 8
MAX_COINS_128 = 8
PRECISION = 10**18
A_PRECISION = 100
FEE_DENOMINATOR = 10**10

# ---- Functions ----

def get_y(i: int, j: int, x: int, xp: list[int], amp: int, D: int) -> int:
    """
    Calculate x[j] if one makes x[i] = x
    """
    assert i != j
    assert 0 <= j < MAX_COINS_128
    assert 0 <= i < MAX_COINS_128

    S_ = 0
    c = D
    Ann = amp * len(xp)

    for _i in range(len(xp)):
        if _i == i:
            _x = x
        elif _i != j:
            _x = xp[_i]
        else:
            continue
        S_ += _x
        c = c * D // (_x * len(xp))

    c = c * D * A_PRECISION // (Ann * len(xp))
    b = S_ + D * A_PRECISION // Ann
    y = D

    for _ in range(255):
        y_prev = y
        y = (y * y + c) // (2 * y + b - D)
        if abs(y - y_prev) <= 1:
            return y

    raise Exception("get_y did not converge")


def get_D(xp: list[int], amp: int) -> int:
    """
    D invariant calculation
    """
    S = sum(xp)
    if S == 0:
        return 0

    D = S
    Ann = amp * len(xp)

    for _ in range(255):
        D_P = D
        for x in xp:
            D_P = D_P * D // x
        D_P //= pow(len(xp), len(xp))
        Dprev = D

        D = ((Ann * S // A_PRECISION + D_P * len(xp)) * D) // (
            (Ann - A_PRECISION) * D // A_PRECISION + (len(xp) + 1) * D_P
        )

        if abs(D - Dprev) <= 1:
            return D

    raise Exception("get_D did not converge")


def get_y_D(A: int, i: int, xp: list[int], D: int) -> int:
    """
    Calculate x[i] if one reduces D
    """
    assert 0 <= i < MAX_COINS_128

    S_ = 0
    c = D
    Ann = A * len(xp)

    for _i in range(len(xp)):
        if _i == i:
            continue
        _x = xp[_i]
        S_ += _x
        c = c * D // (_x * len(xp))

    c = c * D * A_PRECISION // (Ann * len(xp))
    b = S_ + D * A_PRECISION // Ann
    y = D

    for _ in range(255):
        y_prev = y
        y = (y * y + c) // (2 * y + b - D)
        if abs(y - y_prev) <= 1:
            return y

    raise Exception("get_y_D did not converge")


def xp_mem(rates: list[int], balances: list[int]) -> list[int]:
    """
    Scale balances by rates
    """
    return [(rates[i] * balances[i]) // PRECISION for i in range(len(balances))]

