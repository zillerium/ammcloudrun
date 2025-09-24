# classcode/swapdx.py
from .dstate import DState
from .ystated import YStateD   # <-- use the new class

class SwapDx:
    def __init__(self, xb: float, yb: float, A: int):
        self.pool = DState(xb, yb, A)
        self.A = A

    def trade(self, dx: float):
        x0, y0, D = self.pool.x, self.pool.y, self.pool.D
        x_new = x0 + dx

        # Use YStateD with explicit D
        ystate = YStateD(x0, y0, self.A)
        y_new = ystate.get_y(x_new, D)

        dy = y0 - y_new
        loss = dx - dy

        return {
            "x0": x0, "y0": y0,
            "x_new": x_new, "y_new": y_new,
            "dx": dx, "dy": dy,
            "loss": loss, "D": D, "A": self.A,
        }

