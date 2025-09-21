# classcode/calcprice_derivative.py
import csv
import matplotlib.pyplot as plt
from uploader import upload_file
from classcode.plotamm import PlotAMM

class CalcPriceDerivative(PlotAMM):
    """
    Extends PlotAMM to compute price derivatives (dP/dx) for n=2.
    Saves CSV with columns: x, y, delta, dpdx,
    plus a plot of dp/dx vs x.
    """

    def compute_dpdx(self, x: float, y: float, dy_dx: float) -> float:
        """Compute dP/dx using the full expanded formula."""
        A = self.A
        D = self.pool.D

        numerator = D**3 * (
            32*A*(x**3)*y*dy_dx
            - 16*A*(x**2)*(y**2)*dy_dx
            + 16*A*(x**2)*(y**2)
            - 32*A*x*(y**3)
            + (D**3)*x*dy_dx
            - (D**3)*y
        )

        denominator = (x**2) * (
            256*(A**2)*(x**2)*(y**4)
            + 32*A*(D**3)*x*(y**2)
            + (D**6)
        )

        return numerator / denominator

    def generate_csv_with_derivative_price(self):
        rows = self.run_test()

        derivative_rows = []
        dpdx_values = []
        for (x, y, delta) in rows:
            dy_dx = -1  # placeholder, you can compute directly if needed
            dpdx = self.compute_dpdx(x, y, dy_dx)
            derivative_rows.append([x, y, delta, dpdx])
            dpdx_values.append(dpdx)

        # Save CSV locally
        with open(self.csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "y", "delta", "dpdx"])
            writer.writerows(derivative_rows)
        print(f"✅ CSV with derivative price saved locally at {self.csv_file}")

        # Upload CSV to S3
        csv_result = upload_file(self.csv_file, self.csv_remote)
        print("✅ CSV upload result:", csv_result)

        # --- Plot dp/dx vs. x ---
        plt.figure(figsize=(8, 6))
        plt.plot(self.x_values, dpdx_values, label=f"dP/dx (A={self.A})")
        plt.title("StableSwap Price Derivative Curve")
        plt.xlabel("x")
        plt.ylabel("dP/dx")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xlim(200_000, 1_800_000)
        plt.ylim(-0.075e-5, 0.0)   # show only 0 down to -0.2×10^-5

        plt.tight_layout()
        plt.savefig(self.plot_file)
        print(f"✅ Derivative price plot saved locally at {self.plot_file}")

        plot_result = upload_file(self.plot_file, self.plot_remote)
        print("✅ Plot upload result:", plot_result)

        return {"csv": csv_result, "plot": plot_result}

