import numpy as np
import matplotlib.pyplot as plt
from classcode.curve_pool import CurveStableSwap2Pool
from uploader import upload_file

def plot_single_curve(
    out_file="/tmp/stableswap_simple.png",
    remote_name="stableswap_simple.png",
    A=100,
    scaling=1000,
    liquidity=2_000_000,
):
    """
    Plot StableSwap invariant curve with a straight-line overlay for comparison.
    """
    # initialize pool
    pool = CurveStableSwap2Pool(liquidity // 2, liquidity // 2, A=A)
    D0 = pool.D   # invariant at balanced state

    # x range
    factor = int(liquidity / 20)
    x_values = np.linspace(factor, liquidity - factor, 200)

    curve_y = []
    for x in x_values:
        try:
            pool.D = D0   # keep invariant fixed
            y_curve = pool._get_y(x)
            curve_y.append(y_curve)
        except Exception:
            curve_y.append(np.nan)

    # straight line overlay: y = total_liquidity - x
    straight_y = liquidity - x_values

    # plot
    plt.figure(figsize=(10, 6))
    plt.plot(x_values/scaling, np.array(curve_y)/scaling, 'b-', label=f'StableSwap A={A}')
    plt.plot(x_values/scaling, straight_y/scaling, 'k--', label="Straight line y = L - x")

    # balanced point
    plt.plot(liquidity/2/scaling, liquidity/2/scaling, 'ro', label="Balanced Point")

    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel(f'Token Y Balance (÷{scaling})')
    plt.title(f'StableSwap Curve vs Straight Line (A={A})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # save locally
    plt.savefig(out_file)
    print(f"✅ Plot saved locally at {out_file}")

    # upload to S3
    result = upload_file(out_file, remote_name)
    print("✅ Upload result:", result)

    return result


if __name__ == "__main__":
    url_info = plot_single_curve()
    print("🌍 File available at:", url_info.get("url"))

