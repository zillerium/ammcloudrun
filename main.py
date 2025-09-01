import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
import os
from flask import Flask, jsonify, request
from storage.uploader import upload_file   # your working uploader


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

def plot_invariant_curve(out_file="/tmp/stableswap2.png", A1=10, A2=100, A3=1000, scaling=1000):

    """
    Visualize the actual StableSwap curve vs other AMM curves
    """
    # Initialize pools with same liquidity
    total_liquidity = 2_000_000
    curve_a100 = CurveStableSwap2Pool(1_000_000, 1_000_000, A=A2)   # A2
    curve_a10 = CurveStableSwap2Pool(1_000_000, 1_000_000, A=A1)    # A1
    curve_a1000 = CurveStableSwap2Pool(1_000_000, 1_000_000, A=A3)  # A3

    # Generate x values
    x_values = np.linspace(100_000, 1_900_000, 1000)
    
    curve_y_a100 = []
    curve_y_a10 = []
    curve_y_a1000 = []
    constant_product_y = []
    
    # Calculate corresponding y values for each x
    k = 1_000_000 * 1_000_000  # Constant product k
    
    for x in x_values:
        try:
            # Curve with different A values
            y_100 = curve_a100._get_y(x)
            y_10 = curve_a10._get_y(x)
            y_1000 = curve_a1000._get_y(x)
            
            curve_y_a100.append(y_100)
            curve_y_a10.append(y_10)
            curve_y_a1000.append(y_1000)
            
            # Constant product (Uniswap)
            y_cp = k / x
            constant_product_y.append(y_cp)
            
        except:
            curve_y_a100.append(np.nan)
            curve_y_a10.append(np.nan)
            curve_y_a1000.append(np.nan)
            constant_product_y.append(np.nan)
    
    # Plot the curves
    plt.figure(figsize=(12, 8))
  
    plt.plot(x_values/scaling, np.array(curve_y_a10)/scaling, 'b--', label=f'Curve A={A1}', linewidth=2)
    plt.plot(x_values/scaling, np.array(curve_y_a100)/scaling, 'b-', label=f'Curve A={A2}', linewidth=2)
    plt.plot(x_values/scaling, np.array(curve_y_a1000)/scaling, 'g-', label=f'Curve A={A3}', linewidth=2)
    plt.plot(x_values/scaling, np.array(constant_product_y)/scaling, 'r--', label='Constant Product (Uniswap)', linewidth=2)
    
    plt.plot(1_000_000/scaling, 1_000_000/scaling, 'ro', markersize=8, label='Balanced Point')

    
    # Add balance point
    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel(f'Token Y Balance (÷{scaling})')

    plt.title('AMM Invariant Curves Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
   
    #plt.xlim(100, 3000)
    #plt.ylim(100, 3000)
    
    plt.xlim(100, total_liquidity/scaling - 100)
    plt.ylim(100, total_liquidity/scaling - 100)
    diag_x = np.linspace(100, total_liquidity/scaling - 100, 100)

    # Add diagonal line for reference
    plt.plot(diag_x, diag_x, 'k:', alpha=0.5, label='x = y line')
    
    plt.tight_layout()
    plt.savefig(out_file)

    # --- New: slippage calc for A2 ---
    delta_x = x_values[1] - x_values[0]

    slippages = []
    for i in range(len(x_values) - 1):
        dx = x_values[i+1] - x_values[i]
        dy_actual = curve_y_a100[i+1] - curve_y_a100[i]
        spot_price = curve_y_a100[i] / x_values[i]   # ≈1 at balance
        expected_delta_y = dx * spot_price
        slippages.append((dy_actual - expected_delta_y) / scaling)  # scale here

    plt.figure(figsize=(12, 6))
    plt.plot(x_values[:-1]/scaling, slippages, 'm-', label=f'Slippage A={A2}')
    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel('Slippage (Δy - Δx)')
    plt.title(f'Slippage Curve for A={A2}, Δx={int(delta_x)}')

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file.replace(".png", "") + "-A2.png")
    slippages_A2 = slippages   # ✅ store for later

    # --- Slippage calc for A1 ---
    delta_x = x_values[1] - x_values[0]
    slippages = []
    for i in range(len(x_values) - 1):
        dx = x_values[i+1] - x_values[i]
        dy_actual = curve_y_a10[i+1] - curve_y_a10[i]
        spot_price = curve_y_a10[i] / x_values[i]
        expected_delta_y = dx * spot_price
        slippages.append((dy_actual - expected_delta_y) / scaling)

    plt.figure(figsize=(12, 6))
    plt.plot(x_values[:-1]/scaling, slippages, 'c-', label=f'Slippage A={A1}')
    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel('Slippage (Δy - Δx)')
    plt.title(f'Slippage Curve for A={A1}, Δx={int(delta_x)}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file.replace(".png", "") + "-A1.png")
    slippages_A1 = slippages   # ✅ store for later

    # --- Slippage calc for A2 (already working) ---
    # [your existing A2 block here]

    # --- Slippage calc for A3 ---
    slippages = []
    for i in range(len(x_values) - 1):
        dx = x_values[i+1] - x_values[i]
        dy_actual = curve_y_a1000[i+1] - curve_y_a1000[i]
        spot_price = curve_y_a1000[i] / x_values[i]
        expected_delta_y = dx * spot_price
        slippages.append((dy_actual - expected_delta_y) / scaling)

    plt.figure(figsize=(12, 6))
    plt.plot(x_values[:-1]/scaling, slippages, 'g-', label=f'Slippage A={A3}')
    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel('Slippage (Δy - Δx)')
    plt.title(f'Slippage Curve for A={A3}, Δx={int(delta_x)}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file.replace(".png", "") + "-A3.png")
    slippages_A3 = slippages   # ✅ store for later

    # --- Slippage calc for CPMM ---
    slippages = []
    for i in range(len(x_values) - 1):
        dx = x_values[i+1] - x_values[i]
        dy_actual = constant_product_y[i+1] - constant_product_y[i]
        spot_price = constant_product_y[i] / x_values[i]
        expected_delta_y = dx * spot_price
        slippages.append((dy_actual - expected_delta_y) / scaling)

    plt.figure(figsize=(12, 6))
    plt.plot(x_values[:-1]/scaling, slippages, 'r-', label='Slippage CPMM')
    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel('Slippage (Δy - Δx)')
    plt.title(f'Slippage Curve for CPMM, Δx={int(delta_x)}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file.replace(".png", "") + "-CPMM.png")
    slippages_CPMM = slippages   # ✅ store for later

    # --- Superimposed slippage plot (ALL) ---
    plt.figure(figsize=(12, 6))
    plt.plot(x_values[:-1]/scaling, slippages_A1, 'b--', label=f'Slippage A={A1}')
    plt.plot(x_values[:-1]/scaling, slippages_A2, 'm-',  label=f'Slippage A={A2}')
    plt.plot(x_values[:-1]/scaling, slippages_A3, 'g-',  label=f'Slippage A={A3}')
    plt.plot(x_values[:-1]/scaling, slippages_CPMM, 'r--', label='Slippage CPMM')

    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel(f'Slippage (Δy - Δx) ÷{scaling}')
    plt.title(f'Slippage Comparison, Δx={int(delta_x)}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_file.replace(".png", "") + "-ALL.png")




def demonstrate_curve_behavior():
    """
    Show how StableSwap behaves differently from constant product
    """
    print("=== Curve StableSwap vs Constant Product Comparison ===")
    
    # Initialize pools
    initial_x = initial_y = 1_000_000
    curve_pool = CurveStableSwap2Pool(initial_x, initial_y, A=100)
    
    print(f"Initial balances: X = ${initial_x:,}, Y = ${initial_y:,}")
    print(f"Curve invariant D = {curve_pool.D:,.0f}")
    print(f"Constant product k = {initial_x * initial_y:,}")
    
    test_amounts = [10_000, 50_000, 100_000, 250_000, 500_000]
    
    print(f"\n{'Amount':<10} {'Curve Output':<15} {'CP Output':<15} {'Curve Impact':<15} {'CP Impact':<15}")
    print("-" * 75)
    
    for amount in test_amounts:
        # Curve output
        curve_output = curve_pool.get_dy(amount)
        curve_impact = curve_pool.get_price_impact(amount)
        
        # Constant product output (x * y = k)
        k = initial_x * initial_y
        new_x = initial_x + amount
        new_y = k / new_x
        cp_output = initial_y - new_y
        cp_impact = abs(1 - (cp_output/amount)) * 100
        
        print(f"${amount/1000:>7.0f}k {curve_output:>12.2f} {cp_output:>12.2f} {curve_impact:>12.4f}% {cp_impact:>12.4f}%")

def test_extreme_imbalance():
    """
    Test how StableSwap handles extreme imbalances
    """
    print(f"\n=== Testing Extreme Imbalance ===")
    
    # Start balanced
    pool = CurveStableSwap2Pool(1_000_000, 1_000_000, A=100)
    print(f"Balanced pool: X = ${pool.x:,.0f}, Y = ${pool.y:,.0f}")
    
    # Make several large swaps to create imbalance
    large_swaps = [200_000, 200_000, 200_000]
    
    for i, swap_amount in enumerate(large_swaps):
        dy = pool.swap_x_for_y(swap_amount)
        price_impact = (1 - dy/swap_amount) * 100
        
        print(f"Swap {i+1}: ${swap_amount:,} X -> ${dy:.2f} Y (Impact: {price_impact:.3f}%)")
        print(f"  New balances: X = ${pool.x:,.0f}, Y = ${pool.y:,.0f}")
        print(f"  Ratio X/Y = {pool.x/pool.y:.3f}")

app = Flask(__name__)

@app.route("/store_stableswap", methods=["POST"])
def store_stableswap():
    filename = request.args.get("filename", "stableswap23.png")
    local_file = f"/tmp/{filename}"

    # NEW: read A values from query params
    A1 = int(request.args.get("A1", 10))
    A2 = int(request.args.get("A2", 100))
    A3 = int(request.args.get("A3", 1000))
    scaling = int(request.args.get("scaling", 1000))

    print(f"🟢 Generating StableSwap curve: {local_file} with A1={A1}, A2={A2}, A3={A3}, scaling={scaling}")
    plot_invariant_curve(local_file, A1, A2, A3, scaling)

    print(f"🟢 Uploading {local_file} to S3 as {filename}")
    result = upload_file(local_file, filename)

    slippage_file = local_file.replace(".png", "") + "-A2.png"
    slippage_name = filename.replace(".png", "") + "-A2.png"
    print(f"🟢 Uploading {slippage_file} to S3 as {slippage_name}")
    result_slip = upload_file(slippage_file, slippage_name)

    print(f"🟢 Uploading {local_file} to S3 as {filename}")
    result = upload_file(local_file, filename)

    # --- Upload slippage A1 ---
    slippage_file_A1 = local_file.replace(".png", "") + "-A1.png"
    slippage_name_A1 = filename.replace(".png", "") + "-A1.png"
    print(f"🟢 Uploading {slippage_file_A1} to S3 as {slippage_name_A1}")
    result_slip_A1 = upload_file(slippage_file_A1, slippage_name_A1)

    # --- Upload slippage A2 ---
    slippage_file_A2 = local_file.replace(".png", "") + "-A2.png"
    slippage_name_A2 = filename.replace(".png", "") + "-A2.png"
    print(f"🟢 Uploading {slippage_file_A2} to S3 as {slippage_name_A2}")
    result_slip_A2 = upload_file(slippage_file_A2, slippage_name_A2)

    # --- Upload slippage A3 ---
    slippage_file_A3 = local_file.replace(".png", "") + "-A3.png"
    slippage_name_A3 = filename.replace(".png", "") + "-A3.png"
    print(f"🟢 Uploading {slippage_file_A3} to S3 as {slippage_name_A3}")
    result_slip_A3 = upload_file(slippage_file_A3, slippage_name_A3)

    # --- Upload slippage CPMM ---
    slippage_file_CPMM = local_file.replace(".png", "") + "-CPMM.png"
    slippage_name_CPMM = filename.replace(".png", "") + "-CPMM.png"
    print(f"🟢 Uploading {slippage_file_CPMM} to S3 as {slippage_name_CPMM}")
    result_slip_CPMM = upload_file(slippage_file_CPMM, slippage_name_CPMM)

    # --- Upload slippage ALL ---
    slippage_file_ALL = local_file.replace(".png", "") + "-ALL.png"
    slippage_name_ALL = filename.replace(".png", "") + "-ALL.png"
    print(f"🟢 Uploading {slippage_file_ALL} to S3 as {slippage_name_ALL}")
    result_slip_ALL = upload_file(slippage_file_ALL, slippage_name_ALL)

    return jsonify({
        "main": result,
        "slippage_A1": result_slip_A1,
        "slippage_A2": result_slip_A2,
        "slippage_A3": result_slip_A3,
        "slippage_CPMM": result_slip_CPMM,
        "slippage_ALL": result_slip_ALL
    })



if __name__ == "__main__":
    # When run directly → start Flask API, no auto-plot
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port) 


