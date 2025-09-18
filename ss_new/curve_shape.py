# curve_shape.py
import math
from maths_calc_D import MathsCalcD

def solve_y(x: float, A: float, D: float) -> float:
    b = (4*A*x + D - 4*A*D) / (4*A)
    c = -D**3 / (16*A*x)
    disc = b**2 - 4*c
    if disc < 0:
        raise ValueError("No real solution for y")
    y = (-b + math.sqrt(disc)) / 2
    return y

def generate_curve(L=1_000_000, A=100, n_points=20):
    # balanced start
    D = MathsCalcD(L/2, L/2, A)
    results = []
    step = L // (n_points + 1)
    for i in range(1, n_points):
        x = i * step
        try:
            y = solve_y(x, A, D)
            results.append((x, y))
        except Exception:
            pass
    return results

if __name__ == "__main__":
    data = generate_curve()
    print("x,y")
    for x, y in data:
        print(f"{x},{y}")

