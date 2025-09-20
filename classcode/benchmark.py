# classcode/benchmark.py
import numpy as np
from classcode.ystate import YState
from classcode.checkstates import CheckStates

class BenchmarkAMM:
    def __init__(self, xb=1_000_000, yb=1_000_000, A=100, n=200,
                 csv_file="/tmp/stableswap.csv", csv_remote="stableswap.csv",
                 plot_file="/tmp/stableswap.png", plot_remote="stableswap.png"):
        self.xb = xb
        self.yb = yb
        self.A = A
        self.n = n
        self.csv_file = csv_file
        self.csv_remote = csv_remote
        self.plot_file = plot_file
        self.plot_remote = plot_remote

        self.pool = YState(self.xb, self.yb, self.A)
        self.checker = CheckStates(self.A, self.pool.D)
        ## self.x_values = np.linspace(self.xb / 2, self.xb * 1.5, self.n)
        self.x_values = np.linspace(self.xb / 10, self.xb *4 , self.n)

        self.y_values = []
        self.delta_values = []

    def run_test(self):
        rows = []
        for x in self.x_values:
            y = self.pool.get_y(x)
            delta = self.checker.delta(x, y)
            rows.append([x, y, delta])
            self.y_values.append(y)
            self.delta_values.append(delta)
        return rows

