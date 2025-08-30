import numpy as np
import matplotlib.pyplot as plt

def generate_cpmm_plot(filename="example.png"):
    x0, y0 = 1000, 1000
    k = x0 * y0

    x_values = np.linspace(100, 2000, 10)  # 10 sample points
    y_values = [k / x for x in x_values]

    plt.figure(figsize=(6, 4))
    plt.plot(x_values, y_values, 'b-', linewidth=2, label="CPMM (xy=k)")
    plt.scatter([x0], [y0], color="red", label="Initial point")

    plt.title("Simple CPMM Curve")
    plt.xlabel("Token X Balance")
    plt.ylabel("Token Y Balance")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

