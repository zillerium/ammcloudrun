# test_range_L1M.py
import math
from maths_calc_D import MathsCalcD

def calc_dy(x: float, y: float, dx: float, A: float):
    """
    Calculate dy for n=2 StableSwap given x, y, dx, A.
    """
    D = MathsCalcD(x, y, A)
    x_new = x + dx

    b = (4*A*x_new + D - 4*A*D) / (4*A)
    c = -D**3 / (16*A*x_new)

    disc = b**2 - 4*c
    if disc < 0:
        raise ValueError("No real solution for y")

    y_new = (-b + math.sqrt(disc)) / 2
    dy = y - y_new
    return D, y_new, dy

def run_tests(L=1_000_000, dx=10_000, A=100, n_points=10):
    print(f"\n--- Range Test (L={L}, dx={dx}, A={A}) ---\n")
    step = L // (n_points + 1)  # avoid x=0 and y=0
    for i in range(1, n_points+1):
        x = i * step
        y = L - x
        try:
            D, y_new, dy = calc_dy(x, y, dx, A)
            print(f"x={x:8.0f}, y={y:8.0f}, x+dx={x+dx:8.0f}, y_new={y_new:12.2f}, dy={dy:12.6f}")
        except Exception as e:
            print(f"x={x}, y={y}, error={e}")

if __name__ == "__main__":
    run_tests(L=1_000_000, dx=10_000, A=100)

