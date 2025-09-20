# generate_csv.py
from classcode.plotamm import PlotAMM
from classcode.plotmulti import PlotMultiAMM

def main():
    # --- Single A example ---
    amm = PlotAMM(
        xb=1_000_000,
        yb=1_000_000,
        A=100,
        n=200,
        csv_file="/tmp/stableswap_a100.csv",
        csv_remote="stableswap_a100.csv",
        plot_file="/tmp/stableswap_a100.png",
        plot_remote="stableswap_a100.png",
    )
    amm.generate_csv_and_plot()

    # --- Multi A example ---
    multi = PlotMultiAMM(
        xb=1_000_000,
        yb=1_000_000,
        A_list=[1, 10, 100, 1000],
        n=200,
        plot_file="/tmp/stableswap_a1-1000.png",
        plot_remote="stableswap_a1-1000.png",
    )
    multi.generate_plot()

if __name__ == "__main__":
    main()

