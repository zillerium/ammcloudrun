# test_plot.py
import numpy as np
import matplotlib.pyplot as plt
from stableswap_pool import CurveStableSwap2Pool

def plot_invariant_curve(out_file: str = "stableswap_test.png"):
    # Initialize pools with same liquidity
    curve_a100 = CurveStableSwap2Pool(1_000_000, 1_000_000, A=100)
    curve_a10 = CurveStableSwap2Pool(1_000_000, 1_000_000, A=10)
    curve_a1000 = CurveStableSwap2Pool(1_000_000, 1_000_000, A=1000)

    x_values = np.linspace(100_000, 1_900_000, 1000)
    k = 1_000_000 * 1_000_000  # constant product

    y10, y100, y1000, ycp = [], [], [], []
    for x in x_values:
        try:
            y10.append(curve_a10._get_y(x))
            y100.append(curve_a100._get_y(x))
            y1000.append(curve_a1000._get_y(x))
            ycp.append(k / x)
        except Exception as e:
            print("⚠️ Exception at x =", x, ":", e)
            y10.append(np.nan)
            y100.append(np.nan)
            y1000.append(np.nan)
            ycp.append(np.nan)

    plt.figure(figsize=(12, 8))
    plt.plot(x_values/1000, np.array(y10)/1000, 'b--', label='Curve A=10', linewidth=2)
    plt.plot(x_values/1000, np.array(y100)/1000, 'b-', label='Curve A=100', linewidth=2)
    plt.plot(x_values/1000, np.array(y1000)/1000, 'g-', label='Curve A=1000', linewidth=2)
    plt.plot(x_values/1000, np.array(ycp)/1000, 'r--', label='Constant Product', linewidth=2)
    plt.plot(1000, 1000, 'ro', markersize=8, label='Balanced Point')
    plt.xlabel("Token X Balance (thousands)")
    plt.ylabel("Token Y Balance (thousands)")
    plt.title("AMM Invariant Curves Comparison")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()
    print(f"✅ Saved test plot to {out_file}")

if __name__ == "__main__":
    plot_invariant_curve()

