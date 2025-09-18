import time
from typing import List
from .constants import Constants
from .math_utils import MathUtils
from .erc20_base import ERC20Base
from .oracle_manager import OracleManager

class CurveStableSwapNG:
    def __init__(
        self,
        name: str,
        symbol: str,
        A: int,
        fee: int,
        offpeg_fee_multiplier: int,
        ma_exp_time: int,
        coins: List[str],
        rate_multipliers: List[int],
        asset_types: List[int],
        method_ids: List[bytes],
        oracles: List[str],
        factory_admin: str = "mock_admin",
        factory_fee_receiver: str = "mock_receiver",
        block_timestamp: int = None
    ):
        self.N_COINS = len(coins)
        self.coins = coins
        self.asset_types = asset_types
        self.pool_contains_rebasing_tokens = 2 in asset_types
        self.rate_multipliers = rate_multipliers
        self.stored_balances = [0] * self.N_COINS
        self.admin_balances = [0] * self.N_COINS
        self.fee = fee
        self.offpeg_fee_multiplier = offpeg_fee_multiplier
        self.factory = {"admin": factory_admin, "fee_receiver": factory_fee_receiver}
        self.block_timestamp = block_timestamp or int(time.time())
        self.erc20 = ERC20Base(name, symbol)
        self.math_utils = MathUtils()
        self.oracle_manager = OracleManager(ma_exp_time, 62324, self.block_timestamp)
        self.initial_A = A * Constants.A_PRECISION
        self.future_A = self.initial_A
        self.initial_A_time = self.block_timestamp
        self.future_A_time = self.block_timestamp
        self.events = []
        # Initialize rate_oracles, call_amount, scale_factor as needed

    def _A(self) -> int:
        t1 = self.future_A_time
        A1 = self.future_A
        if self.block_timestamp < t1:
            A0 = self.initial_A
            t0 = self.initial_A_time
            if A1 > A0:
                return A0 + (A1 - A0) * (self.block_timestamp - t0) // (t1 - t0)
            else:
                return A0 - (A0 - A1) * (self.block_timestamp - t0) // (t1 - t0)
        return A1

    def _stored_rates(self) -> List[int]:
        rates = self.rate_multipliers.copy()
        # Mock oracle calls (e.g., for asset_type 1 or 3)
        for i in range(self.N_COINS):
            if self.asset_types[i] == 1:
                rates[i] = (rates[i] * 10**18) // Constants.PRECISION  # Mock oracle fetch
            elif self.asset_types[i] == 3:
                rates[i] = (rates[i] * 10**18) // Constants.PRECISION  # Mock ERC4626 convertToAssets
        return rates

    def _balances(self) -> List[int]:
        result = []
        for i in range(self.N_COINS):
            balance = self.erc20.token_balances.get(self.coins[i], 0) - self.admin_balances[i]
            result.append(balance)
        return result

    def exchange(self, i: int, j: int, dx: int, min_dy: int, receiver: str, sender: str) -> int:
        assert i != j and dx > 0
        rates = self._stored_rates()
        old_balances = self._balances()
        xp = self._xp_mem(rates, old_balances)
        dx_received = self._transfer_in(i, dx, sender, False)
        x = xp[i] + (dx_received * rates[i]) // Constants.PRECISION
        dy = self._exchange_internal(x, xp, rates, i, j)
        assert dy >= min_dy, "Exchange resulted in fewer coins than expected"
        self._transfer_out(j, dy, receiver)
        self._log_event("TokenExchange", {"buyer": sender, "sold_id": i, "tokens_sold": dx, "bought_id": j, "tokens_bought": dy})
        return dy

    def _exchange_internal(self, x: int, xp: List[int], rates: List[int], i: int, j: int) -> int:
        amp = self._A()
        D = self.math_utils.get_D(xp, amp)
        y = self.math_utils.get_y(i, j, x, xp, amp, D)
        dy = xp[j] - y - 1
        dy_fee = (dy * self._dynamic_fee((xp[i] + x) // 2, (xp[j] + y) // 2)) // Constants.FEE_DENOMINATOR
        dy = (dy - dy_fee) * Constants.PRECISION // rates[j]
        self.admin_balances[j] += (dy_fee * Constants.ADMIN_FEE // Constants.FEE_DENOMINATOR) * Constants.PRECISION // rates[j]
        xp[i] = x
        xp[j] = y
        self.oracle_manager.upkeep_oracles(xp, amp, D, self.block_timestamp)
        return dy

    def _dynamic_fee(self, xpi: int, xpj: int, base_fee: int = None) -> int:
        if self.offpeg_fee_multiplier <= Constants.FEE_DENOMINATOR:
            return self.fee
        base_fee = base_fee or (self.fee * Constants.MAX_COINS) // (4 * (Constants.MAX_COINS - 1))
        xps2 = (xpi + xpj) ** 2
        return (self.offpeg_fee_multiplier * base_fee) // (
            ((self.offpeg_fee_multiplier - Constants.FEE_DENOMINATOR) * 4 * xpi * xpj) // xps2 + Constants.FEE_DENOMINATOR
        )

    def _xp_mem(self, rates: List[int], balances: List[int]) -> List[int]:
        return [(rates[i] * balances[i]) // Constants.PRECISION for i in range(self.N_COINS)]

    def _transfer_in(self, coin_idx: int, dx: int, sender: str, expect_optimistic: bool) -> int:
        coin = self.coins[coin_idx]
        if expect_optimistic:
            dx_received = dx  # Mock: assume tokens already sent
        else:
            self.erc20.transfer(sender, self, dx)
            dx_received = dx
        self.stored_balances[coin_idx] += dx_received
        self.erc20.token_balances[coin] = self.erc20.token_balances.get(coin, 0) + dx_received
        return dx_received

    def _transfer_out(self, coin_idx: int, amount: int, receiver: str):
        coin = self.coins[coin_idx]
        self.stored_balances[coin_idx] -= amount
        self.erc20.token_balances[coin] = self.erc20.token_balances.get(coin, 0) - amount
        self.erc20.transfer(self, receiver, amount)

    def _log_event(self, event_name: str, params: dict):
        self.events.append({"event": event_name, "params": params})
        print(f"Event {event_name}: {params}")
