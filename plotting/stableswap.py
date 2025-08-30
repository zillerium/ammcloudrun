import numpy as np
import matplotlib.pyplot as plt

class CurveStableSwap2Pool:
    """
    Correct Curve v1 StableSwap AMM implementation for 2 assets
    """

    def __init__(self, balance_x: float, balance_y: float, A: int = 100, fee: float = 0.0004):
        self.x = float(balance_x)
        self.y = float(balance_y)
        self.A = A
        self.fee = fee
        self.D = self._calculate_D()

    def _calculate_D(self, x: float = None, y: float = None) -> float:
        if x is None:
            x = self.x
        if y is None:
            y = self.y
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

    def _get_y(self, x_new: float) -> float:
        D = self.D
        Ann = self.A * 4
        S = x_new
        c = D * D * D / (4 * Ann * x_new)
        b = S + D / Ann
        y_prev = D
        for _ in range(255):
            y = y_prev
            y_prev = (y * y + c) / (2 * y + b - D)
            if abs(y - y_prev) <= 1:
                break
        return y_prev

    def _get_x(self, y_new: float) -> float:
        D = self.D
        Ann = self.A * 4
        S = y_new
        c = D * D * D / (4 * Ann * y_new)
        b = S + D / Ann
        x_prev = D
        for _ in range(255):
            x = x_prev
            x_prev = (x * x + c) / (2 * x + b - D)
            if abs(x - x_prev) <= 1:
                break
        return x_prev

    def get_dy(self, dx: float) -> float:
        x_new = self.x + dx
        y_new = self._get_y(x_new)
        dy = self.y - y_new
        return max(0, dy * (1 - self.fee))

    def get_dx(self, dy: float) -> float:
        y_new = self.y - dy / (1 - self.fee)
        x_new = self._get_x(y_new)
        dx = x_new - self.x
        return max(0, dx)

    def swap_x_for_y(self, dx: float) -> float:
        dy = self.get_dy(dx)
        self.x += dx
        self.y -= dy
        self.D = self._calculate_D()
        return dy

    def swap_y_for_x(self, dy: float) -> float:
        dx = self.get_dx(dy)
        self.y += dy
        self.x -= dx
        self.D = self._calculate_D()
        return dx

    def get_spot_price(self) -> float:
        small_amount = 1.0
        return self.get_dy(small_amount) / small_amount

    def get_price_impact(self, dx: float) -> float:
        dy = self.get_dy(dx)
        average_price = dy / dx
        spot_price = self.get_spot_price()
        if spot_price > 0:
            return abs(1 - average_price / spot_price) * 100
        return 0


def generate_stableswap_plot(filename="/tmp/stableswap.png"):
    """
    Save a plot comparing StableSwap vs CPMM invariant curves.
    """
    curve_a10   = CurveStableSwap2Pool(1_000_000, 1_000_000, A=10)
    curve_a100  = CurveStableSwap2Pool(1_000_000, 1_000_000, A=100)
    curve_a1000 = CurveStableSwap2Pool(1_000_000, 1_000_000, A=1000)

    x_values = np.linspace(100_000, 1_900_000, 1000)
    k = 1_000_000 * 1_000_000

    curve_y_a10, curve_y_a100, curve_y_a1000, cp_y = [], [], [], []

    for x in x_values:
        try:
            curve_y_a10.append(curve_a10._get_y(x))
            curve_y_a100.append(curve_a100._get_y(x))
            curve_y_a1000.append(curve_a1000._get_y(x))
            cp_y.append(k / x)
        except Exception:
            curve_y_a10.append(np.nan)
            curve_y_a100.append(np.nan)
            curve_y_a1000.append(np.nan)
            cp_y.append(np.nan)

    plt.figure(figsize=(12, 8))
    plt.plot(x_values/1000, np.array(curve_y_a10)/1000,   'b--', label="Curve A=10", linewidth=2)
    plt.plot(x_values/1000, np.array(curve_y_a100)/1000,  'b-',  label="Curve A=100", linewidth=2)
    plt.plot(x_values/1000, np.array(curve_y_a1000)/1000, 'g-',  label="Curve A=1000", linewidth=2)
    plt.plot(x_values/1000, np.array(cp_y)/1000,          'r--', label="Constant Product (Uniswap)", linewidth=2)

    plt.plot(1000, 1000, 'ro', markersize=8, label="Balanced Point")
    diag_x = np.linspace(100, 1900, 100)
    plt.plot(diag_x, diag_x, 'k:', alpha=0.5, label="x = y line")

    plt.xlabel("Token X Balance (thousands)")
    plt.ylabel("Token Y Balance (thousands)")
    plt.title("AMM Invariant Curves Comparison")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

