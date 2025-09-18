# main.py
from amm_math import get_D, get_y, get_y_D, xp_mem

def main():
    # ---- Test setup ----
    # 2-coin pool, both with 18 decimals
    rates = [10**18, 10**18]                 # no scaling
    balances = [1000 * 10**18, 1000 * 10**18] # 1000 units of each
    amp = 100                                # amplification factor

    # ---- Step 1: scale balances ----
    xp = xp_mem(rates, balances)
    print("xp:", xp)

    # ---- Step 2: calculate invariant D ----
    D = get_D(xp, amp)
    print("D:", D)

    # ---- Step 3: simulate swap impact ----
    # pretend we add 100 units of coin 0
    x_new = xp[0] + 100 * 10**18
    y_new = get_y(0, 1, x_new, xp, amp, D)
    print("y after adding 100 of coin0:", y_new)

    # ---- Step 4: test get_y_D ----
    # reduce D slightly and check coin 1 balance
    D_reduced = D - 10**18
    y_from_D = get_y_D(amp, 1, xp, D_reduced)
    print("coin1 balance from reduced D:", y_from_D)

if __name__ == "__main__":
    main()

