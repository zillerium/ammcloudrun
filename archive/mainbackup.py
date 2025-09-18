import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
import os
from flask import Flask, jsonify, request
from storage.uploader import upload_file   # your working uploader
import csv

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
def save_slippage_csv(x_values, slippages, csv_file):
    """Save slippage values to CSV at given path."""
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x_value", "slippage"])
        for x, s in zip(x_values[:-1], slippages):
            writer.writerow([x, s])
    return csv_file


def compute_and_plot_slippage(x_values, y_values, scaling, label, plot_file, csv_file):
    """Compute slippages, plot curve into plot_file, and save CSV into csv_file."""
    slippages = []
    for i in range(len(x_values) - 1):
        price_t   = y_values[i]   / x_values[i]
        price_tp1 = y_values[i+1] / x_values[i+1]
        slippages.append((price_tp1 - price_t)*10000)

    # Plot slippage curve
    plt.figure(figsize=(12, 6))
    plt.plot(x_values[:-1]/scaling, slippages, 'm-', label=f'Slippage {label}')
    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel('Slippage (ΔP = P[t+1] - P[t])')
    plt.title(f'Slippage Curve for {label}, Δx={int(x_values[1]-x_values[0])}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(plot_file)
    save_slippage_csv(x_values, slippages, csv_file)

    return slippages


def plot_invariant_curve(out_file="/tmp/stableswap2.png", A1=10, A2=100, A3=1000, scaling=1000, liquidity=2_000_000, all_files=None):

    """
    Visualize the actual StableSwap curve vs other AMM curves
    """
    # Initialize pools with same liquidity
    total_liquidity = liquidity
    curve_a100 = CurveStableSwap2Pool(liquidity // 2, liquidity // 2, A=A1)
    curve_a10 = CurveStableSwap2Pool(liquidity // 2, liquidity // 2, A=A2)
    curve_a1000 = CurveStableSwap2Pool(liquidity // 2, liquidity // 2, A=A3)

    # Define percentage band (e.g., 4 for 4%)
    P = 2

    # Midpoint (balanced liquidity)
    mid = liquidity / 2

    # Band edges
    lower = mid * (1 - P/100)
    upper = mid * (1 + P/100)

    # Generate x values only within the band
    ## x_values = np.linspace(lower, upper, 1000)
    x_values = np.arange(lower, upper + 1, 4)

    curve_y_a100 = []
    curve_y_a10 = []
    curve_y_a1000 = []
    constant_product_y = []
    
    # Calculate corresponding y values for each x
    k = (liquidity // 2) * (liquidity // 2)

    print(f"===== k value '{k}'")
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
            print(f"  CPMM point: x={x}, y={y_cp}")
 
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
    
    plt.plot(liquidity/scaling, liquidity/scaling, 'ro', markersize=8, label='Balanced Point')
    
    # Add balance point
    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel(f'Token Y Balance (÷{scaling})')

    plt.title('AMM Invariant Curves Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
   
    plt.xlim(lower/scaling, upper/scaling)
    plt.ylim(lower/scaling, upper/scaling)
 
    diag_x = np.linspace(100, total_liquidity/scaling - 100, 100)

    # Add diagonal line for reference
    plt.plot(diag_x, diag_x, 'k:', alpha=0.5, label='x = y line')
    
    plt.tight_layout()
    plt.savefig(all_files["plots"])

    # --- Slippage calc for A2 ---
    slippages_A2 = compute_and_plot_slippage(
        x_values=x_values,
        y_values=curve_y_a100,
        scaling=scaling,
        label="A2",
        plot_file=all_files["slippageA2"],
        csv_file=all_files["csvslippageA2"]
    )

    # --- Slippage calc for A1 ---
    slippages_A1 = compute_and_plot_slippage(
        x_values=x_values,
        y_values=curve_y_a10,
        scaling=scaling,
        label="A1",
        plot_file=all_files["slippageA1"],
        csv_file=all_files["csvslippageA1"]
    )

    # --- Slippage calc for A3 ---
    slippages_A3 = compute_and_plot_slippage(
        x_values=x_values,
        y_values=curve_y_a1000,
        scaling=scaling,
        label="A3",
        plot_file=all_files["slippageA3"],
        csv_file=all_files["csvslippageA3"]
    )

    # --- Slippage calc for CPMM ---
    slippages_CPMM = compute_and_plot_slippage(
        x_values=x_values,
        y_values=constant_product_y,
        scaling=scaling,
        label="CPMM",
        plot_file=all_files["slippageCPMM"],
        csv_file=all_files["csvslippageCPMM"]
    )

    # --- Superimposed slippage plot (ALL) ---
    plt.figure(figsize=(12, 6))
    plt.plot(x_values[:-1]/scaling, slippages_A1, 'b--', label=f'Slippage A={A1}')
    plt.plot(x_values[:-1]/scaling, slippages_A2, 'm-',  label=f'Slippage A={A2}')
    plt.plot(x_values[:-1]/scaling, slippages_A3, 'g-',  label=f'Slippage A={A3}')
    plt.plot(x_values[:-1]/scaling, slippages_CPMM, 'r--', label='Slippage CPMM')

    plt.xlabel(f'Token X Balance (÷{scaling})')
    plt.ylabel(f'Slippage (Δy - Δx) ÷{scaling}')
    plt.title(f'Slippage Comparison ')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(all_files["slippageALL"])

app = Flask(__name__)

@app.route("/store_stableswap", methods=["POST"])
def store_stableswap():
    filename = request.args.get("filename", "stableswap23.png")
    local_file = f"/tmp/{filename}"

    # read params
    A1 = int(request.args.get("A1", 10))
    A2 = int(request.args.get("A2", 100))
    A3 = int(request.args.get("A3", 1000))
    scaling = int(request.args.get("scaling", 1000))
    liquidity = int(request.args.get("liquidity", 2_000_000))

    # build all target files
    fileStem = local_file.replace(".png", "")

    all_files = {
        "plots":           fileStem + ".png",
        "slippageA1":     fileStem + "-A1.png",
        "slippageA2":     fileStem + "-A2.png",
        "slippageA3":     fileStem + "-A3.png",
        "slippageCPMM":   fileStem + "-CPMM.png",
        "slippageALL":    fileStem + "-ALL.png",
        "csvslippageA1":          fileStem + "-slippage-A1.csv",
        "csvslippageA2":          fileStem + "-slippage-A2.csv",
        "csvslippageA3":          fileStem + "-slippage-A3.csv",
        "csvslippageCPMM":        fileStem + "-slippage-CPMM.csv",
    }

    # generate plots + CSVs
    plot_invariant_curve(local_file, A1, A2, A3, scaling, liquidity, all_files)

    # debug: show what was generated
    prefix = filename.replace(".png", "")
    print(f"DEBUG: Looking for files in /tmp starting with '{prefix}'")
    for f in os.listdir("/tmp"):
        if f.startswith(prefix):
            path = os.path.join("/tmp", f)
            size = os.path.getsize(path)
            print(f" - {path} ({size} bytes)")
    
    results = {}
    for key, path in all_files.items():
        name = os.path.basename(path)
        results[key] = upload_file(path, name)

    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

