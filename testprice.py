# test_price_independent.py
import csv

def compute_price_formula(x, y, A, D):
    numerator = 4 * A + (D**3) / (4 * (x**2) * y)
    denominator = 4 * A + (D**3) / (4 * x * (y**2))
    return numerator / denominator

def test_prices_from_csv(
    csv_file="/tmp/stableswap_price_a100.csv",
    xb=1_000_000, yb=1_000_000, A=100, tolerance=1e-9
):
    # recompute D once from balanced state
    D = xb + yb   # ✅ simple approximation for 2 tokens at balance

    all_passed = True
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            x = float(row["x"])
            y = float(row["y"])
            expected = float(row["p"])

            calc_p = compute_price_formula(x, y, A, D)

            if abs(calc_p - expected) > tolerance:
                print(f"❌ Row {i}: x={x}, mismatch: got {calc_p}, expected {expected}")
                all_passed = False
            else:
                if i <= 5:  # show only first few successes
                    print(f"✅ Row {i}: OK {calc_p:.12f} ≈ {expected:.12f}")

    if all_passed:
        print("🎉 All independent price tests passed!")
    else:
        print("⚠️ Some mismatches found.")

if __name__ == "__main__":
    test_prices_from_csv()

