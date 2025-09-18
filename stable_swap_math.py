class StableSwapMath:
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
  
