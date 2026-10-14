"""Regenera las figuras del Capítulo 4 a partir del CSV maestro y de la estimación
geométrica de primer orden del intervalo I_L. El ancho numérico de I_L se lee de
datos/derivados/intervalos_L_z.csv, que escribe analysis/reproducir_capitulo4.py.

Las repeticiones técnicas se promedian por combinación réplica--posición antes de
calcular los errores (Sección 3.7); los registros sin valor (ArUco no detectado)
se omiten.
"""
import csv
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "anexos" / "csv-maestro-re-run.csv"
OUT = ROOT / "figuras"
OUT.mkdir(exist_ok=True)

COLORS = {"A": "#C0392B", "A′": "#E67E22", "B": "#2E86C1", "C": "#1E8449"}
MARKERS = {"A": "o", "A′": "^", "B": "s", "C": "D"}
METHODS = ["A", "A′", "B", "C"]
POS = [5, 11, 17, 23]
REPLICAS = ["R1", "R2", "R3", "R4", "R5", "R6"]

# ---------- Errores con signo por combinación réplica--posición ----------
_vals = defaultdict(list)
_ref = {}
with open(CSV, encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if not r["lt_mm"]:
            continue
        key = (r["method"], r["replicate_id"], int(r["position_mm"]) // 10)
        _vals[key].append((float(r["lt_mm"]), float(r["pc_mm"])))
        _ref[r["replicate_id"]] = (float(r["lt_reference_mm"]), float(r["pc_reference_mm"]))

# ERR[m][medida] -> matriz (posición x réplica) de errores con signo, en mm
ERR = {m: {k: np.array([[np.mean([v[i] for v in _vals[(m, rep, p)]]) - _ref[rep][i]
                         for rep in REPLICAS] for p in POS])
           for i, k in enumerate(("LT", "PC"))}
       for m in METHODS}

# Tabla 12 (MAE en mm) y Tabla 13 (MAE de LT por posición, mm)
MAE_LT = {m: float(np.abs(ERR[m]["LT"]).mean()) for m in METHODS}
MAE_PC = {m: float(np.abs(ERR[m]["PC"]).mean()) for m in METHODS}
MAE_LT_POS = {m: list(np.abs(ERR[m]["LT"]).mean(axis=1)) for m in METHODS}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "axes.axisbelow": True,
})

def fmt(v):
    return f"{v:.2f}".replace(".", ",")

# ---------- Figura 15: MAE por método (LT y PC) ----------
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

# ---------- Figura 16: MAE de LT por método y profundidad ----------
fig, ax = plt.subplots(figsize=(6.4, 3.6))
for m in METHODS:
    ax.plot(POS, MAE_LT_POS[m], marker=MARKERS[m], ms=5.5, mec="white", mew=0.6,
            color=COLORS[m], label=m, lw=1.8)
ax.set_xlabel("Distancia nominal de la réplica al vidrio (cm)")
ax.set_ylabel("MAE de LT (mm)")
ax.set_xticks(POS)
ax.set_xlim(3.5, 26.5)
ax.legend(title="Método", frameon=False, ncol=4, loc="upper left")
fig.tight_layout()
# Rótulos del último punto, separados verticalmente para que no se pisen
fig.canvas.draw()
to_pt = ax.transData.transform
y_pt = sorted(((to_pt((POS[-1], MAE_LT_POS[m][-1]))[1], m) for m in METHODS))
placed = []
for y, m in y_pt:
    placed.append((max(y, placed[-1][0] + 14) if placed else y, y, m))
for y_new, y, m in placed:
    ax.annotate(f"{m}: {fmt(MAE_LT_POS[m][-1])}", (POS[-1], MAE_LT_POS[m][-1]),
                xytext=(7, (y_new - y) * 72 / fig.dpi), textcoords="offset points",
                va="center", fontsize=8.5, color="0.2")
fig.savefig(OUT / "fig4_2_mae_lt_profundidad.pdf")
fig.savefig(OUT / "fig4_2_mae_lt_profundidad.png", dpi=200)
plt.close(fig)

# ---------- Figura 17: error con signo por combinación réplica--posición ----------
# A va en su propio panel porque su escala (hasta -80 mm) ocultaría a los demás.
fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.4), gridspec_kw={"width_ratios": [1, 2.2]})
groups = (["A"], ["A′", "B", "C"])
for row, k in enumerate(("LT", "PC")):
    for col, ms in enumerate(groups):
        ax = axes[row, col]
        ax.axhline(0, color="0.35", lw=0.9, zorder=1)
        for j, m in enumerate(ms):
            dx = (j - (len(ms) - 1) / 2) * 1.5
            e = ERR[m][k]
            for i, p in enumerate(POS):
                ax.scatter(np.full(len(REPLICAS), p + dx), e[i], s=26, marker=MARKERS[m],
                           color=COLORS[m], edgecolor="white", linewidth=0.6, zorder=3,
                           label=m if (i == 0 and row == 0) else None)
                ax.plot([p + dx - 0.55, p + dx + 0.55], [e[i].mean()] * 2,
                        color="0.15", lw=1.4, zorder=4)
        ax.set_xticks(POS)
        ax.set_xlim(2.5, 25.5)
        ax.grid(axis="x", visible=False)
        if row == 1:
            ax.set_xlabel("Distancia al vidrio (cm)")
        if col == 0:
            ax.set_ylabel(f"Error con signo de {k} (mm)")
        if row == 0:
            ax.set_title("A" if col == 0 else "A′, B y C (escala ampliada)", fontsize=10)
handles, labels = [], []
for ax in axes[0]:
    h, l = ax.get_legend_handles_labels()
    handles += h; labels += l
handles.append(plt.Line2D([], [], color="0.15", lw=1.4))
labels.append("Media por posición")
fig.legend(handles, labels, loc="lower center", ncol=5, frameon=False, fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "fig4_errores_combinaciones.pdf")
fig.savefig(OUT / "fig4_errores_combinaciones.png", dpi=200)
plt.close(fig)

# ---------- Figura 21: captura real con los cuatro puntos marcados ----------
# Las imágenes originales están en datos/imagenes (ruta configurable con FISHMETER_IMAGES).
import os
IMAGES = Path(os.environ.get("FISHMETER_IMAGES", ROOT / "datos" / "imagenes"))
CAPTURE = "R3-REP1-230.jpg"
if (IMAGES / CAPTURE).exists():
    with open(CSV, encoding="utf-8") as fh:
        row = next(r for r in csv.DictReader(fh) if r["image_id"] == CAPTURE and r["method"] == "C")
    pts = {i: (float(row[f"p{i}_x_px"]), float(row[f"p{i}_y_px"])) for i in range(1, 5)}
    # Todas las réplicas miran a la derecha: el punto longitudinal de mayor x es el hocico.
    snout, tail = sorted((1, 2), key=lambda i: pts[i][0], reverse=True)
    names = {snout: "hocico", tail: "extremo caudal", 3: "perfil dorsal", 4: "perfil ventral"}
    img = plt.imread(IMAGES / CAPTURE)
    xs = [p[0] for p in pts.values()]; ys = [p[1] for p in pts.values()]
    x0, x1 = int(min(xs) - 180), int(max(xs) + 180)
    y0, y1 = int(min(ys) - 160), int(max(ys) + 160)
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.imshow(img[y0:y1, x0:x1])
    ax.annotate("", xy=np.subtract(pts[snout], (x0, y0)), xytext=np.subtract(pts[tail], (x0, y0)),
                arrowprops={"arrowstyle": "-", "color": "#F4D03F", "lw": 1.4, "ls": "--"})
    offsets = {snout: (10, -14), tail: (8, 14), 3: (10, 8), 4: (10, -8)}
    for i, (x, y) in pts.items():
        ax.scatter([x - x0], [y - y0], s=40, color="white", edgecolor="black", linewidth=1.0, zorder=3)
        ax.annotate(names[i], (x - x0, y - y0), xytext=offsets[i], textcoords="offset points",
                    ha="left", va="center", fontsize=9, color="white",
                    bbox={"facecolor": "#222222", "alpha": 0.7, "pad": 1.5, "edgecolor": "none"})
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(OUT / "fig4_captura_R3_230.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig4_captura_R3_230.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

# ---------- Estimación geométrica de primer orden ----------
d, t, n_g, n_w = 230.0, 4.0, 1.5, 1.333
D = lambda z: d + t / n_g + z / n_w          # distancia efectiva paraxial (mm)
L_ref = 140.0                                  # longitud típica de réplica (mm)

# Error predicho de A (escala fijada en el vidrio, z = 0)
pred_A = {z: L_ref * (D(0) / D(z) - 1) for z in (50, 110, 170, 230)}
obs_A = {z: float(ERR["A"]["LT"][i].mean()) for i, z in enumerate((50, 110, 170, 230))}

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
    f.write(f"Diferencia B-C por separacion: {np.round(diff_BC, 2)}\n")
    f.write(f"Pendiente (MAE_B - MAE_C) vs separacion: {np.polyfit([0,6,12,18], diff_BC, 1)[0]:.2f} mm/cm\n")

# Ancho numérico de I_L (% de la LT de calibre): media por posición de la corrida de
# L(z) con C sobre las 72 capturas (analysis/reproducir_capitulo4.py)
INTERVALS = ROOT / "datos" / "derivados" / "intervalos_L_z.csv"
if not INTERVALS.exists():
    raise SystemExit(f"Falta {INTERVALS}: ejecutar antes analysis/reproducir_capitulo4.py")
with open(INTERVALS, encoding="utf-8") as fh:
    _iv = list(csv.DictReader(fh))
num = {label: [float(np.mean([float(r["ancho_num_pct"]) for r in _iv
                              if r["escenario"] == key and int(r["position_mm"]) == int(z)]))
               for z in z_true]
       for key, label in (("0-30 cm", "z desconocida en toda la pecera (0–30 cm)"),
                          ("+-3 cm", "z conocida con ±3 cm"),
                          ("+-1 cm", "z conocida con ±1 cm"))}

# ---------- Figura 18: ancho relativo del intervalo ----------
fig, ax = plt.subplots(figsize=(6.4, 3.6))
cols = ["#7B241C", "#B9770E", "#1E8449"]
x = np.arange(len(z_true)); w = 0.26
for i, (k, v) in enumerate(num.items()):
    bars = ax.bar(x + (i - 1) * w, v, w, label=k, color=cols[i])
    for b, val, ana in zip(bars, v, scen[k]):
        ax.text(b.get_x() + b.get_width() / 2, max(val, ana) + 1.8, f"{val:.0f}", ha="center", fontsize=8)
    ax.plot(x + (i - 1) * w, scen[k], ls="none", marker="_", ms=11, mew=1.6, color="black",
            label="Predicción de primer orden" if i == 0 else None)
MAPE_Ap = 100 * float(np.mean([abs(ERR["A′"]["LT"][i, j]) / _ref[rep][0]
                               for i in range(len(POS)) for j, rep in enumerate(REPLICAS)]))
ax.axhline(MAPE_Ap, color=COLORS["A′"], ls="--", lw=1,
           label=f"MAPE de A′ ({MAPE_Ap:.1f} %)".replace(".", ","))
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
