# classcode/ystate.py
from .dstate import DState

class YState(DState):
    """
    Computes y given x, based on fixed A and D inherited from DState.
    """
    def get_y(self, x_new: float) -> float:
        Ann = self.A * 4
        D = self.D
        c = D**3 / (4 * Ann * x_new)
        b = x_new + D / Ann

        y_prev = D
        for _ in range(255):
            y = y_prev
            y_prev = (y * y + c) / (2 * y + b - D)
            if abs(y - y_prev) <= 1:
                break
        return y_prev

