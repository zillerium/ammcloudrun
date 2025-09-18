class test_D:
    def __init__(self, A: int, x: int, y: int, D: int):
        self.A = A
        self.x = x
        self.y = y
        self.D = D
        self.n = 2  # two-coin pool

    def lhs(self) -> int:
        """Left-hand side of invariant equation"""
        return self.A * self.n**self.n * (self.x + self.y) + self.D

    def rhs(self) -> int:
        """Right-hand side of invariant equation"""
        term1 = self.A * self.D * self.n**self.n
        term2 = self.D**(self.n + 1) // (self.n**self.n * (self.x * self.y))
        return term1 + term2

    def check(self, tolerance: int = 1) -> bool:
        """Check if LHS and RHS are approximately equal (within tolerance)"""
        lhs_val = self.lhs()
        rhs_val = self.rhs()
        print(f"LHS = {lhs_val}")
        print(f"RHS = {rhs_val}")
        return abs(lhs_val - rhs_val) <= tolerance

