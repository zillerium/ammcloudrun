from typing import List

class Constants:
    MAX_COINS = 8
    MAX_COINS_128 = 8
    PRECISION = 10**18
    FEE_DENOMINATOR = 10**10
    A_PRECISION = 100
    MAX_A = 10**6
    MAX_A_CHANGE = 10
    MIN_RAMP_TIME = 86400
    ADMIN_FEE = 5000000000
    MAX_FEE = 5 * 10**9
    ORACLE_BIT_MASK = (2**32 - 1) * 256**28
    ERC1271_MAGIC_VAL = 0x1626ba7e00000000000000000000000000000000000000000000000000000000
    EIP712_TYPEHASH = int.from_bytes(
        hashlib.sha3_256(b"EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)").digest(),
        "big"
    )
    EIP2612_TYPEHASH = int.from_bytes(
        hashlib.sha3_256(b"Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)").digest(),
        "big"
    )
    VERSION = "v7.0.0"
    VERSION_HASH = int.from_bytes(hashlib.sha3_256(VERSION.encode()).digest(), "big")
    DECIMALS = 18
