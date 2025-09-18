import numpy as np
import matplotlib.pyplot as plt
from classcode.curve_pool import CurveStableSwap2Pool
from uploader import upload_file   # 👈 your S3 uploader

def plot_curves_multiA(
    out_file="/tmp/stableswap_multiA.png",
    remote_name="stableswap_multiA.png",
    A_values=(10, 100, 1000),
    scaling=1000,
    liquidity=2_000_000,
):
    """
    Plot StableSwap invariant curves for multiple A values,
    with straight-line overlay for comparison.
    Save locally and upload to S3.
    """
    factor = int(liquidity / 20)
    x_values = np.linspace(factor, liquidity - factor, 400)

    plt.figure(figsize=(10, 6))

    # straight line y = L - x
    straight_y = liquidity - x_values
    plt.plot(x_values/scaling, straight_y/scaling, 'k--', label="Straight line y = L - x")

    for A in A_values:
        pool = CurveStableSwap2Pool(liquidity // 2, liquidity // 2, A=A)
        D0 = pool.D
        curve_y = []

        for x in x_values:
            try:
                pool.D = D0
                y_curve = pool._get_y(x)
                curve_y.append(y_curve)
            except Exception:
                curve_y.append(np.nan)

        plt.plot(x_values/scaling, np.array(curve_y)/scaling, label=f'StableSwap A={A}')

    # balanced point
    plt.plot(liquidity/2/scaling, liquidity/2/scaling, 'ro', label="Balanced Point")

    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel(f'Token Y Balance (÷{scaling})')
    plt.title("StableSwap Curves for Different A Values")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file)
    print(f"✅ Plot saved locally at {out_file}")

    # upload to S3
    result = upload_file(out_file, remote_name)
    print("✅ Upload result:", result)

    return result

if __name__ == "__main__":
    url_info = plot_curves_multiA()
    print("🌍 File available at:", url_info.get("url"))

