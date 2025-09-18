from decimal import Decimal
from curve_stableswap_ng import CurveStableSwapNG
from constants import Constants

def main():
    try:
        # Initialize the pool
        pool = CurveStableSwapNG(
            name="TestPool",
            symbol="TPL",
            A=100,
            fee=4000000,  # 0.04%
            offpeg_fee_multiplier=20000000000,
            ma_exp_time=866,  # 10 min EMA
            coins=["0xTokenA", "0xTokenB"],
            rate_multipliers=[10**18, 10**18],
            asset_types=[0, 0],  # Standard ERC20
            method_ids=[b"", b""],
            oracles=["0xOracleA", "0xOracleB"],
            block_timestamp=1725682200,  # Fixed timestamp for reproducibility (2025-09-07 04:30 AM BST)
        )

        # Mock initial balances for sender and pool
        sender = "0xUser"
        pool.erc20.balanceOf[sender] = 10000 * 10**18  # 10,000 TokenA for sender
        pool.erc20.token_balances["0xTokenA"] = 1000000 * 10**18  # 1M TokenA in pool
        pool.erc20.token_balances["0xTokenB"] = 1000000 * 10**18  # 1M TokenB in pool
        pool.stored_balances = [1000000 * 10**18, 1000000 * 10**18]  # Sync stored balances

        # Perform the exchange
        dx = 1000 * 10**18  # 1000 TokenA
        min_dy = 990 * 10**18  # Expect at least 990 TokenB
        dy = pool.exchange(i=0, j=1, dx=dx, min_dy=min_dy, receiver=sender, sender=sender)

        # Format output with Decimal for precision
        received_tokens = Decimal(dy) / Decimal(10**18)
        print(f"Received: {received_tokens:.18f} tokens")

        # Print events for debugging
        for event in pool.events:
            print(event)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
