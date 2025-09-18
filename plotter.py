import numpy as np
import matplotlib.pyplot as plt
from classcode.calc_y import CalcY
from uploader import upload_file   # 👈 bring in S3 uploader

def plot_curve(
    A=100,
    liquidity=2_000_000,
    out_file="/tmp/stableswap11.png",
    remote_name="stableswap11.png"
):
    """
    Plot one StableSwap invariant curve and upload to AWS S3.
    """
    pool = CalcY(liquidity // 2, liquidity // 2, A=A)
    D0 = pool.refresh_D()   # parent manages D

    ## x_values = np.linspace(liquidity // 20, liquidity - liquidity // 20, 300)
    x_values = np.linspace(2000, liquidity - 2000, 500)
    y_values = [pool.solve_y(x) for x in x_values]

    # --- Plot ---
    plt.figure(figsize=(8, 6))
    plt.plot(x_values, y_values, label=f"StableSwap A={A}")
    plt.plot(x_values, liquidity - x_values, "k--", label="y = L - x")
    plt.legend()
    plt.title("StableSwap Invariant Curve")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file)
    print(f"✅ Plot saved locally at {out_file}")

    # --- Upload to AWS ---
    result = upload_file(out_file, remote_name)
    if "url" in result:
        print(f"🌍 Uploaded to {result['url']}")
    else:
        print("❌ Upload failed:", result)

    return result

if __name__ == "__main__":
    # run a quick demo plot + upload
    result = plot_curve(A=100, liquidity=2_000_000)
    print("✅ Done. Upload info:", result)

