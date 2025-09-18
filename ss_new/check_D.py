from maths_calc_D import MathsCalcD

def check_invariant(x: float, y: float, A: float, D: float):
    """
    Plug values into the n=2 invariant equation and print LHS, RHS.
    """
    lhs = 4 * A * (x + y) + D
    rhs = 4 * A * D + D**3 / (4 * x * y)
    print(f"LHS = {lhs}")
    print(f"RHS = {rhs}")
    print(f"Difference = {lhs - rhs}")

def run_test(x: float, y: float, A: float):
    D = MathsCalcD(x, y, A)
    print("\n--- Test Case ---")
    print(f"x = {x}, y = {y}, A = {A}")
    print(f"Solved D = {D}")
    check_invariant(x, y, A, D)

def main():
    # Balanced pool
    run_test(1_000_000, 1_000_000, A=100)

    # Imbalanced pool
    run_test(1_000_000, 90_000, A=100)

    # Higher amplification
    run_test(1_000_000, 900_000, A=1000)

if __name__ == "__main__":
    main()

