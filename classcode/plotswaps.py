# classcode/plotswaps.py
import csv
import matplotlib.pyplot as plt
from uploader import upload_file
from classcode.swapdx import SwapDx

class PlotSwaps:
    """
    Runs swap tests for a fixed dx across a range of x values.
    Outputs CSV and a loss-vs-x plot.
    """
    def __init__(self, xb=1_000_000, yb=1_000_000, A=100, dx=10_000, n=50,
                 csv_file="/tmp/swaps.csv", csv_remote="swaps.csv",
                 plot_file="/tmp/swaps.png", plot_remote="swaps.png"):
        self.xb = xb
        self.yb = yb
        self.A = A
        self.dx = dx
        self.n = n
        self.csv_file = csv_file
        self.csv_remote = csv_remote
        self.plot_file = plot_file
        self.plot_remote = plot_remote

    def generate_csv_and_plot(self):
        # Initial pool
        xb, yb = self.xb, self.yb
        results = []

        # Run n sequential trades of size dx
        for _ in range(self.n):
            swap = SwapDx(xb, yb, self.A)
            row = swap.trade(self.dx)
            results.append(row)

            # update pool state
            xb, yb = row["x_new"], row["y_new"]

        # Save CSV
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ CSV saved locally at {self.csv_file}")

        csv_result = upload_file(self.csv_file, self.csv_remote)
        print("✅ CSV upload result:", csv_result)

        # Plot loss vs x
        xs = [r["x_new"] for r in results]
        losses = [r["loss"] for r in results]

        plt.figure(figsize=(8, 6))
        plt.plot(xs, losses, label=f"A={self.A}, dx={self.dx}")
        plt.axhline(0, color="k", linestyle="--")
        plt.xlabel("Reserve x")
        plt.ylabel("Trader Loss (dx - dy)")
        plt.title("StableSwap Loss vs Reserve x")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.plot_file)
        print(f"✅ Plot saved locally at {self.plot_file}")

        plot_result = upload_file(self.plot_file, self.plot_remote)
        print("✅ Plot upload result:", plot_result)

        return {"csv": csv_result, "plot": plot_result}

