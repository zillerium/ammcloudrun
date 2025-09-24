# trade.py
from classcode.plotswaps import PlotSwaps

def main():
    # Example run for A=100, dx=10k
    plotter = PlotSwaps(
        xb=1_000_000,
        yb=1_000_000,
        A=100,
        dx=10_000,
        n=50,
        csv_file="/tmp/swaps_a100.csv",
        csv_remote="swaps_a100.csv",
        plot_file="/tmp/swaps_a100.png",
        plot_remote="swaps_a100.png",
    )
    result = plotter.generate_csv_and_plot()
    print("✅ Results:", result)

if __name__ == "__main__":
    main()

