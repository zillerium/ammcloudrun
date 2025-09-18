# small_curve_test.py
import math
from maths_calc_D import MathsCalcD

def solve_y(x: float, A: float, D: float) -> float:
    b = (4*A*x + D - 4*A*D) / (4*A)
    c = -D**3 / (16*A*x)
    disc = b**2 - 4*c
    return (-b + math.sqrt(disc)) / 2

def main():
    L = 200
    A = 100
    D = MathsCalcD(L/2, L/2, A)

    # fine steps near balanced point
    for x in range(1, 201, 10):  # step of 10
        y = solve_y(x, A, D)
        print(f"{x},{y:.6f}")

    # optional: bigger steps beyond
    for x in range(200, 501, 50):
        y = solve_y(x, A, D)
        print(f"{x},{y:.6f}")

if __name__ == "__main__":
    main()

