 


from .calc_d import CalcD

class CurveStableSwap2Pool(CalcD):
    """
    StableSwap 2-pool AMM.
    Inherits CalcD (and thus AMMState).
    """
    def __init__(self, balance_x: float, balance_y: float, A: int = 100, fee: float = 0.0004, method: str = "newton"):
        super().__init__(balance_x, balance_y, A, fee)

        # choose which D calculation to use
        if method == "exact":
            self.D = self._calculate_D_2()
        else:
            self.D = self._calculate_D()
        
    
    def _get_y(self, x_new: float) -> float:
        """
        Given new x balance, solve for y using the invariant
        This solves: 4*A*(x_new + y) + D = 4*A*D + D^3/(4*x_new*y)
        
        Rearranging: y^2 + y*b + c = 0 where:
        b = (4*A*x_new + D - 4*A*D) / 4*A
        c = -D^3 / (16*A*x_new)
        """
        D = self.D
        Ann = self.A * 4
        
        # Solve the quadratic equation ay^2 + by + c = 0
        # After algebraic manipulation of the invariant
        S = x_new
        c = D * D * D / (4 * Ann * x_new)
        b = S + D / Ann
        
        y_prev = D
        # Newton-Raphson to solve for y
        for i in range(255):
            y = y_prev
            y_prev = (y * y + c) / (2 * y + b - D)
            if abs(y - y_prev) <= 1:
                break
                
        return y_prev
    
    def get_dy(self, dx: float) -> float:
        """
        Calculate output amount y for input amount dx
        """
        x_new = self.x + dx
        y_new = self._get_y(x_new)
        dy = self.y - y_new
        
        # Apply trading fee
        dy_after_fee = dy * (1 - self.fee)
        
        return max(0, dy_after_fee)
    
    def get_dx(self, dy: float) -> float:
        """
        Calculate required input x for desired output dy
        """
        y_new = self.y - dy / (1 - self.fee)  # Account for fee
        x_new = self._get_x(y_new)
        dx = x_new - self.x
        
        return max(0, dx)
    
    def _get_x(self, y_new: float) -> float:
        """
        Given new y balance, solve for x using the invariant
        """
        D = self.D
        Ann = self.A * 4
        
        S = y_new
        c = D * D * D / (4 * Ann * y_new)
        b = S + D / Ann
        
        x_prev = D
        for i in range(255):
            x = x_prev
            x_prev = (x * x + c) / (2 * x + b - D)
            if abs(x - x_prev) <= 1:
                break
                
        return x_prev
    
    def swap_x_for_y(self, dx: float) -> float:
        """Execute swap: input dx, receive dy"""
        dy = self.get_dy(dx)
        
        self.x += dx
        self.y -= dy
        self.D = self._calculate_D()
        
        return dy
    
    def swap_y_for_x(self, dy: float) -> float:
        """Execute swap: input dy, receive dx"""
        dx = self.get_dx(dy)
        
        self.y += dy
        self.x -= dx
        self.D = self._calculate_D()
        
        return dx
    
    def get_spot_price(self) -> float:
        """Get instantaneous price dy/dx"""
        small_amount = 1.0
        return self.get_dy(small_amount) / small_amount
    
    def get_price_impact(self, dx: float) -> float:
        """Calculate price impact percentage"""
        dy = self.get_dy(dx)
        average_price = dy / dx
        spot_price = self.get_spot_price()
        
        if spot_price > 0:
            return abs(1 - average_price / spot_price) * 100
        return 0

 
