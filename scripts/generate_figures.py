"""Regenerates the result figures from the sensor data in the project presentation."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

out = Path(__file__).resolve().parent.parent / "results"
C = np.arange(24, 36)
F = C * 9 / 5 + 32
Vs = np.array([.27, .28, .29, .30, .31, .32, .33, .34, .35, .36, .37, .38])

# 1. LM35 calibration
slope, icpt = np.polyfit(F, Vs, 1)
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(F, Vs, "o", label="measured")
ax.plot(F, slope * F + icpt, "-", label=f"fit: Vs = {slope:.4f}·T + ({icpt:.3f})")
ax.set(xlabel="Temperature (°F)", ylabel="Sensor voltage Vs (V)", title="LM35 sensor calibration")
ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(out / "sensor-calibration.png", dpi=160)

# 2. Scale & shift: VT = alpha + beta*Vs
beta = (3.5 - 1.5) / (0.38 - 0.27)
alpha = 1.5 - beta * 0.27
VH, VL = 3.7, 1.23
vs = np.linspace(.25, .40, 100)
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(vs, alpha + beta * vs, label=f"VT = {alpha:.2f} + {beta:.2f}·Vs")
ax.axhline(VH, color="tab:red", ls="--", label=f"VH = {VH} V")
ax.axhline(VL, color="tab:blue", ls="--", label=f"VL = {VL} V")
ax.set(xlabel="Sensor voltage Vs (V)", ylabel="Scaled voltage VT (V)", title="Scale-and-shift stage")
ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(out / "scale-shift-transfer.png", dpi=160)

# 3. Relay hysteresis (simulated with the D-flip-flop logic)
def next_state(vt, q):
    if vt > VH: return 0   # too hot  -> relay OFF (hold-off band logic)
    if vt < VL: return 1   # too cold -> relay ON
    return q               # in band  -> hold
t = np.linspace(0, 60, 600)
T_F = 84 + 16 * np.sin(2 * np.pi * t / 30)           # illustrative temperature swing
VT = alpha + beta * (slope * T_F + icpt)
q, Q = 1, []
for v in VT:
    q = next_state(v, q); Q.append(q)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7, 5), sharex=True)
a1.plot(t, VT); a1.axhline(VH, color="tab:red", ls="--"); a1.axhline(VL, color="tab:blue", ls="--")
a1.set_ylabel("VT (V)"); a1.set_title("Two-threshold (hysteresis) control — illustrative simulation")
a2.step(t, Q, where="post"); a2.set(ylabel="Relay state", xlabel="Time (arb. units)", yticks=[0, 1])
for a in (a1, a2): a.grid(alpha=.3)
fig.tight_layout(); fig.savefig(out / "hysteresis-simulation.png", dpi=160)

print(f"slope={slope:.5f} icpt={icpt:.4f} alpha={alpha:.2f} beta={beta:.2f}")
print("VH->", ((VH-alpha)/beta-icpt)/slope, "F ; VL->", ((VL-alpha)/beta-icpt)/slope, "F")
