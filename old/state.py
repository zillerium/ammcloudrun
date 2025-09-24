class AMMState:
    """
    Base class to hold common AMM state variables.
    """
    def __init__(self, balance_x: float, balance_y: float, A: int = 100, fee: float = 0.0004):
        self.x = float(balance_x)
        self.y = float(balance_y)
        self.A = A
        self.fee = fee
        self.D = None   # invariant, calculated later

