from classcode.curve_pool import CurveStableSwap2Pool

def main():
    # initialize pool
    pool = CurveStableSwap2Pool(1_000_000, 1_000_000, A=100)
    print("=== Testing CurveStableSwap2Pool ===")
    print("x:", pool.x)
    print("y:", pool.y)
    print("A:", pool.A)
    print("fee:", pool.fee)
    print("D (invariant):", pool.D)

    # run a simple swap
    dx = 10_000
    dy = pool.swap_x_for_y(dx)
    print(f"\nSwap {dx} X → {dy:.2f} Y")
    print("New balances: x =", pool.x, ", y =", pool.y)
    print("Updated D:", pool.D)

if __name__ == "__main__":
    main()

