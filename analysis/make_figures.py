"""Regenera las figuras del Capítulo 4 a partir de las Tablas 4.2 y 4.3 del libro
y de la estimación geométrica de primer orden del intervalo I_L.

Cuando exista el CSV maestro, reemplazar los diccionarios por lectura directa
(results/master.csv) y conservar el resto del script.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent.parent / "figuras"
OUT.mkdir(exist_ok=True)

COLORS = {"A": "#C0392B", "A′": "#E67E22", "B": "#2E86C1", "C": "#1E8449"}
METHODS = ["A", "A′", "B", "C"]

# Tabla 4.2 (MAE en mm)
MAE_LT = {"A": 37.43, "A′": 3.29, "B": 16.32, "C": 1.22}
MAE_PC = {"A": 9.07, "A′": 1.03, "B": 3.68, "C": 0.56}
# Tabla 4.3 (MAE de LT por posición, mm)
POS = [5, 11, 17, 23]
MAE_LT_POS = {
    "A": [13.77, 32.02, 46.29, 57.64],
    "A′": [3.44, 3.18, 3.44, 3.11],
    "B": [19.43, 17.45, 15.26, 13.16],
    "C": [1.09, 1.41, 1.29, 1.07],
}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "axes.axisbelow": True,
})

def fmt(v):
    return f"{v:.2f}".replace(".", ",")

# ---------- Figura 4.1: MAE por método (LT y PC) ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
for ax, data, title in zip(axes, (MAE_LT, MAE_PC), ("Longitud total (LT)", "Profundidad corporal (PC)")):
    vals = [data[m] for m in METHODS]
    bars = ax.bar(METHODS, vals, color=[COLORS[m] for m in METHODS], width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + max(vals) * 0.015, fmt(v),
                ha="center", va="bottom", fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.set_ylabel("MAE (mm)")
    ax.set_ylim(0, max(vals) * 1.15)
    ax.grid(axis="x", visible=False)
fig.tight_layout()
fig.savefig(OUT / "fig4_1_mae_por_metodo.pdf")
fig.savefig(OUT / "fig4_1_mae_por_metodo.png", dpi=200)
plt.close(fig)

# ---------- Figura 4.2: MAE de LT por método y profundidad ----------
fig, ax = plt.subplots(figsize=(6.4, 3.6))
for m in METHODS:
    ax.plot(POS, MAE_LT_POS[m], marker="o", color=COLORS[m], label=m, lw=1.8)
    ax.annotate(fmt(MAE_LT_POS[m][-1]), (POS[-1], MAE_LT_POS[m][-1]),
                xytext=(6, 0), textcoords="offset points", va="center", fontsize=8.5, color=COLORS[m])
ax.set_xlabel("Distancia nominal de la réplica al vidrio (cm)")
ax.set_ylabel("MAE de LT (mm)")
ax.set_xticks(POS)
ax.set_xlim(3.5, 25.5)
ax.legend(title="Método", frameon=False, ncol=4, loc="upper left")
fig.tight_layout()
fig.savefig(OUT / "fig4_2_mae_lt_profundidad.pdf")
fig.savefig(OUT / "fig4_2_mae_lt_profundidad.png", dpi=200)
plt.close(fig)

# ---------- Estimación geométrica de primer orden ----------
d, t, n_g, n_w = 230.0, 4.0, 1.5, 1.333
D = lambda z: d + t / n_g + z / n_w          # distancia efectiva paraxial (mm)
L_ref = 140.0                                  # longitud típica de réplica (mm)

# Error predicho de A (escala fijada en el vidrio, z = 0)
pred_A = {z: L_ref * (D(0) / D(z) - 1) for z in (50, 110, 170, 230)}
obs_A = {50: -13.77, 110: -32.02, 170: -46.29, 230: -57.64}

# Ancho relativo de I_L según el conocimiento de z (L(z) ∝ D(z) para C)
z_true = np.array([50, 110, 170, 230], float)
def width(zt, zlo, zhi):
    zlo, zhi = max(zlo, 0.0), min(zhi, 300.0)
    return (D(zhi) - D(zlo)) / D(zt) * 100
scen = {
    "z desconocida en toda la pecera (0–30 cm)": [width(z, 0, 300) for z in z_true],
    "z conocida con ±3 cm": [width(z, z - 30, z + 30) for z in z_true],
    "z conocida con ±1 cm": [width(z, z - 10, z + 10) for z in z_true],
}

with open(OUT / "valores_analiticos.txt", "w", encoding="utf-8") as f:
    f.write("Error predicho de A (mm) para L=140 mm:\n")
    for z in pred_A:
        f.write(f"  z={z} mm: predicho {pred_A[z]:.1f}, observado {obs_A[z]:.2f}, dif {pred_A[z]-obs_A[z]:.1f}\n")
    f.write("Ancho relativo de I_L (% de LT):\n")
    for k, v in scen.items():
        f.write(f"  {k}: " + ", ".join(f"{x:.1f}" for x in v) + "\n")
    f.write(f"Pendiente MAE_A vs separacion: {np.polyfit([0,6,12,18], MAE_LT_POS['A'], 1)[0]:.2f} mm/cm\n")
    diff_BC = np.array(MAE_LT_POS['B']) - np.array(MAE_LT_POS['C'])
    f.write(f"Diferencia B-C por separacion: {diff_BC}\n")
    f.write(f"Pendiente (MAE_B - MAE_C) vs separacion: {np.polyfit([0,6,12,18], diff_BC, 1)[0]:.2f} mm/cm\n")

# Ancho numérico de I_L (% de la LT de calibre): media por posición de la corrida de
# L(z) con C sobre las 72 capturas (Fishmeter, outputs/tesis_pendientes/datos/intervalos_L_z.csv)
num = {
    "z desconocida en toda la pecera (0–30 cm)": [81.78, 71.01, 62.41, 55.55],
    "z conocida con ±3 cm": [16.36, 14.20, 12.48, 11.11],
    "z conocida con ±1 cm": [5.45, 4.73, 4.16, 3.70],
}

# ---------- Figura 4.3: ancho relativo del intervalo ----------
fig, ax = plt.subplots(figsize=(6.4, 3.6))
cols = ["#7B241C", "#B9770E", "#1E8449"]
x = np.arange(len(z_true)); w = 0.26
for i, (k, v) in enumerate(num.items()):
    bars = ax.bar(x + (i - 1) * w, v, w, label=k, color=cols[i])
    for b, val, ana in zip(bars, v, scen[k]):
        ax.text(b.get_x() + b.get_width() / 2, max(val, ana) + 1.8, f"{val:.0f}", ha="center", fontsize=8)
    ax.plot(x + (i - 1) * w, scen[k], ls="none", marker="_", ms=11, mew=1.6, color="black",
            label="Predicción de primer orden" if i == 0 else None)
ax.axhline(2.28, color=COLORS["A′"], ls="--", lw=1, label="MAPE de A′ (2,3 %)")
ax.set_xticks(x); ax.set_xticklabels([f"{int(z/10)} cm" for z in z_true])
ax.set_xlabel("Profundidad real de la réplica")
ax.set_ylabel("Ancho relativo de $I_L$ (% de LT)")
ax.set_ylim(0, 115)
ax.legend(frameon=False, fontsize=8.5, loc="upper right")
ax.grid(axis="x", visible=False)
fig.tight_layout()
fig.savefig(OUT / "fig4_3_ancho_intervalo.pdf")
fig.savefig(OUT / "fig4_3_ancho_intervalo.png", dpi=200)
plt.close(fig)
print(open(OUT / "valores_analiticos.txt", encoding="utf-8").read())
