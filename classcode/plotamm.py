# classcode/plotamm.py
import csv
import matplotlib.pyplot as plt
from uploader import upload_file
from classcode.benchmark import BenchmarkAMM

class PlotAMM(BenchmarkAMM):
    def generate_csv_and_plot(self):
        rows = self.run_test()

        # Save CSV
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "y", "delta"])
            writer.writerows(rows)
        print(f"✅ CSV saved locally at {self.csv_file}")

        csv_result = upload_file(self.csv_file, self.csv_remote)
        print("✅ CSV upload result:", csv_result)

        # Plot
        plt.figure(figsize=(8, 6))
        plt.plot(self.x_values, self.y_values, label=f"StableSwap A={self.A}")
        plt.plot(self.x_values,
                 self.xb + self.yb - self.x_values,
                 "k--", label="y = L - x")
        plt.title("StableSwap Invariant Curve")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.plot_file)
        print(f"✅ Plot saved locally at {self.plot_file}")

        plot_result = upload_file(self.plot_file, self.plot_remote)
        print("✅ Plot upload result:", plot_result)

        return {"csv": csv_result, "plot": plot_result}

