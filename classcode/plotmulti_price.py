# classcode/plotmulti_price.py
import matplotlib.pyplot as plt
from uploader import upload_file
from classcode.calcprice import CalcPrice

class PlotMultiPrice:
    """
    Plot multiple StableSwap price curves for different A values.
    """
    def __init__(self, xb=1_000_000, yb=1_000_000, A_list=None, n=200,
                 plot_file="/tmp/stableswap_multi_price.png",
                 plot_remote="stableswap_multi_price.png"):
        self.xb = xb
        self.yb = yb
        self.A_list = A_list or [1, 10, 100, 1000]
        self.n = n
        self.plot_file = plot_file
        self.plot_remote = plot_remote

    def generate_plot(self):
        plt.figure(figsize=(8, 6))

        for A in self.A_list:
            price_calc = CalcPrice(
                xb=self.xb,
                yb=self.yb,
                A=A,
                n=self.n,
                csv_file=f"/tmp/stableswap_price_a{A}.csv",
                csv_remote=f"stableswap_price_a{A}.csv",
                plot_file=f"/tmp/stableswap_price_a{A}.png",
                plot_remote=f"stableswap_price_a{A}.png",
            )

            rows = price_calc.run_test()
            prices = [price_calc.compute_price(x, y) for (x, y, _) in rows]

            plt.plot(price_calc.x_values, prices, label=f"A={A}")

        plt.axhline(1.0, color="k", linestyle="--", label="Balanced price p=1")
        plt.title(f"StableSwap Price Curves for A={min(self.A_list)}–{max(self.A_list)}")
        plt.xlabel("x")
        plt.ylabel("Price p")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 3)
        plt.tight_layout()
        plt.savefig(self.plot_file)
        print(f"✅ Multi-price plot saved locally at {self.plot_file}")

        result = upload_file(self.plot_file, self.plot_remote)
        print("✅ Upload result:", result)
        return result

