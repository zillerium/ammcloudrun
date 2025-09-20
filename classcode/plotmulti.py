# classcode/plotmulti.py
import matplotlib.pyplot as plt
from uploader import upload_file
from classcode.benchmark import BenchmarkAMM

class PlotMultiAMM:
    """
    Plot multiple StableSwap invariant curves for different A values.
    """
    def __init__(self, xb=1_000_000, yb=1_000_000, A_list=None, n=200,
                 plot_file="/tmp/stableswap_multi.png", plot_remote="stableswap_multi.png"):
        self.xb = xb
        self.yb = yb
        self.A_list = A_list or [1, 10, 100, 1000]
        self.n = n
        self.plot_file = plot_file
        self.plot_remote = plot_remote

    def generate_plot(self):
        plt.figure(figsize=(8, 6))

        # loop over A values and reuse BenchmarkAMM
        for A in self.A_list:
            benchmark = BenchmarkAMM(self.xb, self.yb, A, self.n)
            benchmark.run_test()
            plt.plot(benchmark.x_values, benchmark.y_values, label=f"A={A}")

        # straight-line reference
        #plt.plot(benchmark.x_values,
        #         self.xb + self.yb - benchmark.x_values,
        #         "k--", label="y = L - x")

        rows = benchmark.run_test()

        # keep only positive y values
        x_vals = []
        y_vals = []
        for x, y, _ in rows:
            if y <= 0:
                break
            x_vals.append(x)
            y_vals.append(y)

        plt.plot(x_vals, y_vals, label=f"A={A}")


        plt.title(f"StableSwap Curves for A={min(self.A_list)}–{max(self.A_list)}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.plot_file)
        print(f"✅ Multi-plot saved locally at {self.plot_file}")

        result = upload_file(self.plot_file, self.plot_remote)
        print("✅ Upload result:", result)
        return result

