import math

def MathsCalcD(x: float, y: float, A: float) -> float:
    """
    Solve the StableSwap invariant cubic exactly for n=2.
    Returns the real positive root for D.
    """
    xy = x * y
    
    # Corrected coefficients for the cubic equation D^3 + pD + q = 0
    p = 4 * xy * (4 * A - 1)
    q = -16 * A * xy * (x + y)

    # Discriminant
    discriminant = (q / 2) ** 2 + (p / 3) ** 3

    if discriminant >= 0:
        sqrt_disc = math.sqrt(discriminant)
        u_term = -q / 2 + sqrt_disc
        v_term = -q / 2 - sqrt_disc
        
        # Cube root calculations need to handle negative numbers correctly
        u = u_term**(1/3) if u_term >= 0 else -(-u_term)**(1/3)
        v = v_term**(1/3) if v_term >= 0 else -(-v_term)**(1/3)
        
        root = u + v
    else:
        # Cardano's formula for the irreducible case
        r = math.sqrt(-(p / 3) ** 3)
        phi = math.acos(-q / (2 * r))
        root = 2 * math.sqrt(-p / 3) * math.cos(phi / 3)
    
    return root
