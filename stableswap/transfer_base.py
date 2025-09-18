import time
import hashlib
from typing import Dict
from .constants import Constants

class ERC20Base:
    def __init__(self, name: str, symbol: str, chain_id: int = 1):
        self.name = name
        self.symbol = symbol
        self.balanceOf: Dict[str, int] = {}
        self.allowance: Dict[str, Dict[str, int]] = {}
        self.nonces: Dict[str, int] = {}
        self.total_supply = 0
        self.chain_id = chain_id
        self.name_hash = int.from_bytes(hashlib.sha3_256(name.encode()).digest(), "big")
        self.salt = int.from_bytes(hashlib.sha3_256(str(time.time()).encode()).digest(), "big")  # Mock prevhash
        self.domain_separator = self._domain_separator()

    def _domain_separator(self) -> int:
        return int.from_bytes(
            hashlib.sha3_256(
                self._abi_encode(
                    Constants.EIP712_TYPEHASH,
                    self.name_hash,
                    Constants.VERSION_HASH,
                    self.chain_id,
                    id(self),  # Mock contract address
                    self.salt
                )
            ).digest(),
            "big"
        )

    def _abi_encode(self, *args) -> bytes:
        # Simplified: assume args are pre-encoded or simple types
        return b"".join(str(a).encode() for a in args)  # Mock encoding

    def transfer(self, _from: str, _to: str, value: int) -> bool:
        self.balanceOf[_from] = self.balanceOf.get(_from, 0) - value
        self.balanceOf[_to] = self.balanceOf.get(_to, 0) + value
        self._log_event("Transfer", {"sender": _from, "receiver": _to, "value": value})
        return True

    def transferFrom(self, _from: str, _to: str, value: int) -> bool:
        self.balanceOf[_from] = self.balanceOf.get(_from, 0) - value
        self.balanceOf[_to] = self.balanceOf.get(_to, 0) + value
        allowance = self.allowance.get(_from, {}).get(msg_sender, 0)
        if allowance != 2**256 - 1:
            self.allowance[_from][msg_sender] = allowance - value
            self._log_event("Approval", {"owner": _from, "spender": msg_sender, "value": allowance - value})
        self._log_event("Transfer", {"sender": _from, "receiver": _to, "value": value})
        return True

    def _burnFrom(self, _from: str, amount: int):
        self.total_supply -= amount
        self.balanceOf[_from] = self.balanceOf.get(_from, 0) - amount
        self._log_event("Transfer", {"sender": _from, "receiver": "0x0", "value": amount})

    def _log_event(self, event_name: str, params: dict):
        print(f"Event {event_name}: {params}")  # Replace with logging if needed
