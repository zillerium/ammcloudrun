
class StableSwapPool:

    def get_dy(self, dx: float) -> float:
        """
        Calculates the amount of token Y received for a given amount of token X,
        accounting for the fee.
        
        Args:
            dx (float): The amount of token X to swap in.
            
        Returns:
            float: The net amount of token Y received.
        """
        if dx <= 0:
            raise ValueError("dx must be a positive value.")
        
        # 1. Calculate the new reserve of x
        x_new = self.x + dx
        
        # 2. Solve for the new reserve of y using the quadratic formula
        # The equation to solve is: y^2 + b*y + c = 0
        
        # We derive the quadratic coefficients from the invariant equation
        # 4A(x_new + y) + D = 4AD + D^3 / (4*x_new*y)
        # Rearranging gives: y^2 + (x_new - D*(4A-1)/(4A))y - D^3/(16*A*x_new) = 0
        
        b = x_new - (self.D * (4 * self.A - 1)) / (4 * self.A)
        c = -(self.D**3) / (16 * self.A * x_new)
        
        # Use the quadratic formula to solve for y_new
        discriminant = b**2 - 4 * c
        if discriminant < 0:
            # This should not happen with valid inputs
            raise ValueError("Quadratic discriminant is negative, invalid state.")
            
        y_new = (-b + math.sqrt(discriminant)) / 2
        
        # 3. Calculate the gross output dy (before fees)
        dy_gross = self.y - y_new
        
        # 4. Apply the fee
        dy_net = dy_gross * (1 - self.fee)
        
        # Update the pool's reserves
        self.x = x_new
        self.y = y_new
        
        return dy_net

