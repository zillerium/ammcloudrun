# simple_test.py
import math
from maths_calc_D import MathsCalcD

def calc_dy(x: float, y: float, dx: float, A: float) -> float:
    D = MathsCalcD(x, y, A)
    x_new = x + dx
    b = (4*A*x_new + D - 4*A*D) / (4*A)
    c = -D**3 / (16*A*x_new)
    disc = b**2 - 4*c
    if disc < 0:
        raise ValueError("No real solution for y")
    y_new = (-b + math.sqrt(disc)) / 2
    dy = y - y_new
    return dy, D, y_new

def check_invariant(x: float, y: float, A: float, D: float):
    lhs = 4 * A * (x + y) + D
    rhs = 4 * A * D + D**3 / (4 * x * y)
    diff = lhs - rhs
    print(f"LHS = {lhs}")
    print(f"RHS = {rhs}")
    print(f"Difference = {diff}")
    return diff

def main():
    x, y, dx, A = 1_000_000, 1_000_000, 10_000, 100
    dy, D, y_new = calc_dy(x, y, dx, A)

    print("\n--- Simple Test ---")
    print(f"x = {x}, y = {y}, dx = {dx}, A = {A}")
    print(f"Solved D = {D}")
    print(f"y_new = {y_new}")
    print(f"dy = {dy}")

    print("\n--- Invariant Check ---")
    check_invariant(x + dx, y_new, A, D)

if __name__ == "__main__":
    main()

