# generate_csv.py
import csv
import numpy as np
import matplotlib.pyplot as plt
from classcode.ystate import YState
from classcode.checkstates import CheckStates
from uploader import upload_file


def generate_csv_and_plot(
    xb=1_000_000,
    yb=1_000_000,
    A=100,
    n=200,
    csv_file="/tmp/stableswap_a100.csv",
    csv_remote="stableswap_a100.csv",
    plot_file="/tmp/stableswap_a100.png",
    plot_remote="stableswap_a100.png",
):
    pool = YState(xb, yb, A)
    checker = CheckStates(A, pool.D)

    x_values = np.linspace(xb / 2, xb * 1.5, n)
    rows = []
    y_values = []
    delta_values = []

    for x in x_values:
        y = pool.get_y(x)
        delta = checker.delta(x, y)
        rows.append([x, y, delta])
        y_values.append(y)
        delta_values.append(delta)

    # --- Save CSV locally ---
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "delta"])
        writer.writerows(rows)
    print(f"✅ CSV saved locally at {csv_file}")

    # --- Upload CSV ---
    csv_result = upload_file(csv_file, csv_remote)
    print("✅ CSV upload result:", csv_result)

    # --- Plot curve ---
    plt.figure(figsize=(8, 6))
    plt.plot(x_values, y_values, label=f"StableSwap A={A}")
    plt.plot(x_values, xb + yb - x_values, "k--", label="y = L - x")  # straight-line ref
    plt.title("StableSwap Invariant Curve")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(plot_file)
    print(f"✅ Plot saved locally at {plot_file}")

    # --- Upload PNG ---
    plot_result = upload_file(plot_file, plot_remote)
    print("✅ Plot upload result:", plot_result)

    return {"csv": csv_result, "plot": plot_result}


if __name__ == "__main__":
    result = generate_csv_and_plot()
    print("🌍 Done:", result)

