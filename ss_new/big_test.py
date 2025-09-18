# big_test.py
import math
from maths_calc_D import MathsCalcD

def solve_y(x: float, A: float, D: float) -> float:
    b = (4*A*x + D - 4*A*D) / (4*A)
    c = -D**3 / (16*A*x)
    disc = b**2 - 4*c
    return (-b + math.sqrt(disc)) / 2

def main():
    L = 1_000_000
    A = 100
    D = MathsCalcD(L/2, L/2, A)

    # test for very large x values
    xs = [1_000_000, 10_000_000, 100_000_000, 1_000_000_000]
    for x in xs:
        y = solve_y(x, A, D)
        # output as CSV style
        print(f"{x},{y}")

if __name__ == "__main__":
    main()

