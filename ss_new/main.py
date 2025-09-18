from calc_D import CalcD

def main():
    # 2-coin pool, both coins normalized to 1e18 precision
    balances = [1_000_000 * 10**6, 1_000_000 * 10 * 10**6]
    amp = 1000

    calc = CalcD(n_coins=2)
    D = calc.get_D(balances, amp)

    print("Balances:", balances)
    print("Amp:", amp)
    print("Calculated D:", D)

if __name__ == "__main__":
    main()

