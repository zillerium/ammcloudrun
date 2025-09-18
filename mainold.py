import os
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request
from storage.uploader import upload_file   # your working uploader

# ✅ import the class from the new file
from curve_stableswap_2pool import CurveStableSwap2Pool


def plot_invariant_curve(out_file="/tmp/stableswap2.png", A1=10, A2=100, A3=1000, scaling=1000, liquidity=2_000_000):
    total_liquidity = liquidity

    # ✅ now call the imported class
    curve_a100 = CurveStableSwap2Pool(liquidity // 2, liquidity // 2, A=A1)
    curve_a10 = CurveStableSwap2Pool(liquidity // 2, liquidity // 2, A=A2)
    curve_a1000 = CurveStableSwap2Pool(liquidity // 2, liquidity // 2, A=A3)


app = Flask(__name__)

@app.route("/store_stableswap", methods=["POST"])
def store_stableswap():
    filename = request.args.get("filename", "stableswap23.png")
    local_file = f"/tmp/{filename}"

    A1 = int(request.args.get("A1", 10))
    A2 = int(request.args.get("A2", 100))
    A3 = int(request.args.get("A3", 1000))
    scaling = int(request.args.get("scaling", 1000))
    liquidity = int(request.args.get("liquidity", 2_000_000))
    plot_invariant_curve(local_file, A1, A2, A3, scaling, liquidity)

    return jsonify({
        "status": "ok",
        "filename": filename,
        "path": local_file
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

