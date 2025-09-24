# classcode/ystated.py
from .dstate import DState

class YStateD(DState):
    """
    Variant of YState that allows passing an explicit D
    (so that D is held constant during a swap).
    """
    def get_y(self, x_new: float, D: float) -> float:
        Ann = self.A * 4
        c = D**3 / (4 * Ann * x_new)
        b = x_new + D / Ann

        y_prev = D
        for _ in range(255):
            y = y_prev
            y_prev = (y * y + c) / (2 * y + b - D)
            if abs(y - y_prev) <= 1:
                break
        return y_prev

