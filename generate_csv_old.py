# generate_csv.py
from classcode.plotamm import PlotAMM

def main():
    # Example run: A=5
    amm = PlotAMM(
        xb=1_000_000,
        yb=1_000_000,
        A=5,
        n=200,
        csv_file="/tmp/stableswap_a5.csv",
        csv_remote="stableswap_a5.csv",
        plot_file="/tmp/stableswap_a5.png",
        plot_remote="stableswap_a5.png",
    )

    result = amm.generate_csv_and_plot()
    print("🌍 Done:", result)

if __name__ == "__main__":
    main()

