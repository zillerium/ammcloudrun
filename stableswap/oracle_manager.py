from typing import List, Tuple
from .constants import Constants
from .math_utils import MathUtils

class OracleManager:
    def __init__(self, ma_exp_time: int, D_ma_time: int, block_timestamp: int):
        self.ma_exp_time = ma_exp_time
        self.D_ma_time = D_ma_time
        self.ma_last_time = self._pack_2(block_timestamp, block_timestamp)
        self.last_prices_packed: List[int] = []
        self.last_D_packed = 0
        self.math_utils = MathUtils()

    def _pack_2(self, p1: int, p2: int) -> int:
        assert p1 < 2**128 and p2 < 2**128
        return p1 | (p2 << 128)

    def _unpack_2(self, packed: int) -> Tuple[int, int]:
        return (packed & (2**128 - 1), packed >> 128)

    def _calc_moving_average(self, packed_value: int, averaging_window: int, ma_last_time: int, block_timestamp: int) -> int:
        last_spot_value = packed_value & (2**128 - 1)
        last_ema_value = packed_value >> 128
        if ma_last_time < block_timestamp:
            alpha = self.math_utils.exp(
                -((block_timestamp - ma_last_time) * Constants.PRECISION) // averaging_window
            )
            return (last_spot_value * (Constants.PRECISION - alpha) + last_ema_value * alpha) // Constants.PRECISION
        return last_ema_value

    def upkeep_oracles(self, xp: List[int], amp: int, D: int, block_timestamp: int):
        ma_last_time_unpacked = self._unpack_2(self.ma_last_time)
        last_prices_packed_new = self.last_prices_packed.copy()
        spot_price = self._get_p(xp, amp, D)
        for i in range(len(spot_price)):
            if i >= len(xp) - 1:
                break
            if spot_price[i] != 0:
                last_prices_packed_new[i] = self._pack_2(
                    min(spot_price[i], 2 * Constants.PRECISION),
                    self._calc_moving_average(
                        self.last_prices_packed[i], self.ma_exp_time, ma_last_time_unpacked[0], block_timestamp
                    )
                )
        self.last_prices_packed = last_prices_packed_new
        self.last_D_packed = self._pack_2(
            D, self._calc_moving_average(self.last_D_packed, self.D_ma_time, ma_last_time_unpacked[1], block_timestamp)
        )
        for i in range(2):
            if ma_last_time_unpacked[i] < block_timestamp:
                ma_last_time_unpacked[i] = block_timestamp
        self.ma_last_time = self._pack_2(ma_last_time_unpacked[0], ma_last_time_unpacked[1])

    def _get_p(self, xp: List[int], amp: int, D: int) -> List[int]:
        ANN = amp * Constants.MAX_COINS
        Dr = D // (Constants.MAX_COINS ** Constants.MAX_COINS)
        for x in xp:
            Dr = (Dr * D) // x
        p = [0] * (Constants.MAX_COINS - 1)
        xp0_A = (ANN * xp[0]) // Constants.A_PRECISION
        for i in range(1, len(xp)):
            if i >= len(xp):
                break
            p[i - 1] = (Constants.PRECISION * (xp0_A + (Dr * xp[0] // xp[i]))) // (xp0_A + Dr)
        return p
