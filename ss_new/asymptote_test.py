# asymptote_test.py
import math
from maths_calc_D import MathsCalcD

def solve_y(x: float, A: float, D: float) -> float:
    b = (4*A*x + D - 4*A*D) / (4*A)
    c = -D**3 / (16*A*x)
    disc = b**2 - 4*c
    return (-b + math.sqrt(disc)) / 2

def run_asymptote_test(L=1_000_000, A=100):
    D = MathsCalcD(L/2, L/2, A)
    print(f"Testing asymptote behaviour with L={L}, A={A}\n")
    for x in [100_000, 300_000, 500_000, 700_000, 900_000, 950_000, 990_000, 999_000]:
        try:
            y = solve_y(x, A, D)
            print(f"x={x:>8}, y={y:>12.2f}")
        except Exception as e:
            print(f"x={x:>8}, error={e}")

if __name__ == "__main__":
    run_asymptote_test()

