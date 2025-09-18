

class CurveStableSwap2Pool:
    """
    Correct Curve v1 StableSwap AMM implementation for 2 assets
    
    The actual StableSwap invariant is:
    A*n^n*S + D = A*D*n^n + D^(n+1)/(n^n * prod(x_i))
    
    For 2 assets (n=2):
    4*A*S + D = 4*A*D + D^3/(4*x*y)
    
    Where S = x + y (sum of balances)
    """
    
    def __init__(self, balance_x: float, balance_y: float, A: int = 100, fee: float = 0.0004):
        """
        Initialize StableSwap 2-pool
        """
        self.x = float(balance_x)
        self.y = float(balance_y)
        self.A = A
        self.fee = fee
        self.D = self._calculate_D()
        
    def _calculate_D(self, x: float = None, y: float = None) -> float:
        """
        Calculate invariant D using Newton-Raphson iteration
        This is the critical part that was wrong before
        """
        if x is None:
            x = self.x
        if y is None:
            y = self.y
            
        S = x + y
        if S == 0:
            return 0
            
        D = S  # Initial guess
        Ann = self.A * 4  # A * n^n where n=2, so n^n = 4
        
        # Newton-Raphson iteration to solve for D
        for i in range(255):
            D_P = D
            # For 2 coins: D_P = D^3 / (4*x*y) 
            # But we need to be more careful about the calculation
            D_P = D * D * D / (4 * x * y)
            
            D_prev = D
            # The Newton-Raphson update formula:
            # f(D) = Ann*S + D - Ann*D - D^(n+1)/(n^n * prod(x_i))
            # f'(D) = 1 - Ann - (n+1)*D^n/(n^n * prod(x_i))
            # D_new = D - f(D)/f'(D)
            
            numerator = (Ann * S + D_P * 2) * D
            denominator = (Ann - 1) * D + D_P * 3
            
            D = numerator / denominator
            
            # Check convergence
            if abs(D - D_prev) <= 1:
                break
                
        return D
    
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
 
