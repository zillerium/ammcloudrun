from calc_D import CalcD
from test_D import test_D  # your class above

def run_test(x: int, y: int, A: int):
    calc = CalcD(n_coins=2)
    D = calc.get_D([x, y], A)

    print("\n--- Test Case ---")
    print(f"x = {x}, y = {y}, A = {A}, D = {D}")

    inv_test = test_D(A=A, x=x, y=y, D=D)
    ok = inv_test.check()

    if ok:
        print("✅ Invariant holds within tolerance.")
    else:
        print("❌ Invariant check failed.")

def main():
    # Balanced pool
    run_test(1_000_000 * 10**6, 1_000_000 * 10**6, A=100)

    # Imbalanced pool
    run_test(1_000_000 * 10**6, 90_000 * 10**6, A=100)

    # Higher amplification
    run_test(1_000_000 * 10**6, 900_000 * 10**6, A=1000)

if __name__ == "__main__":
    main()

