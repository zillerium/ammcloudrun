# classcode/calcprice.py
import csv
import matplotlib.pyplot as plt
from uploader import upload_file
from classcode.plotamm import PlotAMM

class CalcPrice(PlotAMM):
    """
    Extends PlotAMM to compute prices for n=2 and
    save CSV with columns: x, y, delta, p,
    plus a price-vs-x plot.
    """

    def compute_price(self, x: float, y: float) -> float:
        D = self.pool.D
        print(f"🔎 Debug: using D = {D} for x={x}, y={y}")
        numerator = 4 * self.A + (D**3) / (4 * (x**2) * y)
        denominator = 4 * self.A + (D**3) / (4 * x * (y**2))
        print(f"🔎 Debug: num and dem num ={numerator} dem={denominator}")
        return numerator / denominator

    def generate_csv_with_price(self):
        rows = self.run_test()

        priced_rows = []
        prices = []
        for (x, y, delta) in rows:
            p = self.compute_price(x, y)
            priced_rows.append([x, y, delta, p])
            prices.append(p)

        # Save CSV locally
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "y", "delta", "p"])
            writer.writerows(priced_rows)
        print(f"✅ CSV with price saved locally at {self.csv_file}")

        # Upload CSV to S3
        csv_result = upload_file(self.csv_file, self.csv_remote)
        print("✅ CSV upload result:", csv_result)

        # --- Plot price vs. x ---
        plt.figure(figsize=(8, 6))
        plt.plot(self.x_values, prices, label=f"Price1 (A={self.A})")
        plt.axhline(1.0, color="k", linestyle="--", label="Balanced price p=1")
        plt.title("StableSwap Price Curve")
        plt.xlabel("x")
        plt.ylabel("Price p")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.plot_file)
        print(f"✅ Price plot saved locally at {self.plot_file}")

        plot_result = upload_file(self.plot_file, self.plot_remote)
        print("✅ Plot upload result:", plot_result)

        return {"csv": csv_result, "plot": plot_result}

