# generate_csv.py
from classcode.plotamm import PlotAMM
from classcode.plotmulti import PlotMultiAMM
from classcode.calcprice import CalcPrice
from classcode.calcprice_derivative import CalcPriceDerivative

from classcode.plotmulti_price import PlotMultiPrice
def main():
    # --- Single A example ---
    amm = PlotAMM(
        xb=1_000_000,
        yb=1_000_000,
        A=1,
        n=200,
        csv_file="/tmp/teststable_a1.csv",
        csv_remote="teststable_a1.csv",
        plot_file="/tmp/teststable_a1.png",
        plot_remote="teststable_a1.png",
    )
    amm.generate_csv_and_plot()

    # --- Multi A example ---
    multi = PlotMultiAMM(
        xb=1_000_000,
        yb=1_000_000,
        A_list=[1, 10, 100, 1000],
        n=200,
        plot_file="/tmp/teststable_a1-1000.png",
        plot_remote="teststable_a1-1000.png",
    )
    multi.generate_plot()

    # --- Price example ---
    price = CalcPrice(
        xb=1_000_000,
        yb=1_000_000,
        A=1,
        n=200,
        csv_file="/tmp/teststable_price_a1.csv",
        csv_remote="teststable_price_a1.csv",
        plot_file="/tmp/teststable_price_a1.png",
        plot_remote="teststable_price_a1.png",
    )
    price.generate_csv_with_price()

    derivative = CalcPriceDerivative(
        xb=1_000_000,
        yb=1_000_000,
        A=1,
        n=200,
        csv_file="/tmp/teststable_derivative_price_a1.csv",
        csv_remote="teststable_derivative_price_a1.csv",
        plot_file="/tmp/teststable_derivative_price_a1.png",
        plot_remote="teststable_derivative_price_a1.png",
    )
    derivative.generate_csv_with_derivative_price()


    # --- Multi Price example ---
    multi_price = PlotMultiPrice(
        xb=1_000_000,
        yb=1_000_000,
        A_list=[1, 10, 100, 1000],
        n=200,
        plot_file="/tmp/teststable_multi_price.png",
        plot_remote="teststable_multi_price.png",
    )
    multi_price.generate_plot()



if __name__ == "__main__":
    main()

