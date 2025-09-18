from .calc_d import CalcD

class CalcY(CalcD):
    """
    Subclass responsible for solving y given x and D.
    """
    def _calculate_y(self, x_new: float, D: float) -> float:
        Ann = self.A * 4
        c = D * D * D / (4 * Ann * x_new)
        b = x_new + D / Ann

        y_prev = D
        for _ in range(255):
            y = y_prev
            y_prev = (y * y + c) / (2 * y + b - D)
            if abs(y - y_prev) <= 1:
                break
        return y_prev

