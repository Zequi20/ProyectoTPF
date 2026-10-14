"""Reproduce las cifras del Capítulo 4 a partir de los datos publicados.

Entradas (todas dentro de este repositorio):
    anexos/csv-maestro-re-run.csv        tabla maestra (288 registros, B recalculado)
    datos/calibraciones/calibration_C_air.yaml, flat_port.yaml

Requiere el código de Fishmeter en la versión de la tesis (etiqueta v1.0-tesis de
https://github.com/Zequi20/FishmeterTPF), instalado con ``pip install -e`` o indicado
con la variable FISHMETER_SRC (ruta a su carpeta src/).

Uso, desde la raíz del proyecto:
    python analysis/reproducir_capitulo4.py

Imprime las Tablas 11 a 14 (sensibilidad, errores por método y por posición,
ancho y cobertura de I_L), los conteos pareados y las pruebas de signos que usa la
Tabla 15, y los límites de Bland--Altman. Escribe:
    datos/derivados/sensibilidad_c.csv, L_z.csv, intervalos_L_z.csv, resumen_capitulo4.json
    figuras/fig4_bland_altman_c.pdf, figuras/fig4_L_z_ejemplos.pdf
"""
import csv
import json
import math
import os
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "anexos" / "csv-maestro-re-run.csv"
CALIB = ROOT / "datos" / "calibraciones"
DERIV = ROOT / "datos" / "derivados"
FIG = ROOT / "figuras"

if os.environ.get("FISHMETER_SRC"):
    sys.path.insert(0, os.environ["FISHMETER_SRC"])
try:
    from fish_morphometry.calibration.air_calibration import load_air_calibration
    from fish_morphometry.geometry.refractive_port import load_manual_flat_port, make_measurement_plane
    from fish_morphometry.methods.c import measure_c
except ImportError:
    sys.exit("No se encontró fish_morphometry: instalar FishmeterTPF (v1.0-tesis) o definir FISHMETER_SRC.")

METHODS = ("A", "A′", "B", "C")
POSITIONS = (50, 110, 170, 230)
COLOR_C = "#1E8449"


# ---------- Lectura y agregación ----------
def read_rows():
    with CSV.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def has_value(row):
    return row["lt_mm"].strip() != ""


def grouped(rows, method, images=None):
    """Promedia las repeticiones técnicas de cada combinación réplica--posición."""
    groups = {}
    for r in rows:
        if r["method"] != method or not has_value(r) or (images is not None and r["image_id"] not in images):
            continue
        groups.setdefault((r["replicate_id"], int(r["position_mm"])), []).append(r)
    out = {}
    for key, rs in sorted(groups.items()):
        rec = {"n": len(rs)}
        for m in ("lt", "pc"):
            est = float(np.mean([float(r[f"{m}_mm"]) for r in rs]))
            ref = float(rs[0][f"{m}_reference_mm"])
            rec.update({f"{m}_mm": est, f"{m}_ref": ref, f"{m}_err": est - ref})
        out[key] = rec
    return out


def metrics(records):
    out = {"n": len(records)}
    for m in ("lt", "pc"):
        e = np.array([r[f"{m}_err"] for r in records]); y = np.array([r[f"{m}_ref"] for r in records])
        out.update({f"sesgo_{m}": float(e.mean()), f"mae_{m}": float(np.abs(e).mean()),
                    f"mape_{m}": float((np.abs(e) / y).mean() * 100)})
    return out


def per_capture(rows, method):
    recs = []
    for r in rows:
        if r["method"] == method and has_value(r):
            recs.append({f"{m}_err": float(r[f"{m}_mm"]) - float(r[f"{m}_reference_mm"]) for m in ("lt", "pc")}
                        | {f"{m}_ref": float(r[f"{m}_reference_mm"]) for m in ("lt", "pc")})
    return metrics(recs)


def common_images(rows):
    by_image = {}
    for r in rows:
        if has_value(r):
            by_image.setdefault(r["image_id"], set()).add(r["method"])
    return {i for i, ms in by_image.items() if ms == set(METHODS)}


def tables(rows, images=None):
    g = {m: grouped(rows, m, images) for m in METHODS}
    t44 = {m: metrics(list(g[m].values())) for m in METHODS}
    t45 = {p: {m: float(np.mean([abs(v["lt_err"]) for (rep, pos), v in g[m].items() if pos == p]))
               for m in METHODS} for p in POSITIONS}
    return g, t44, t45


# ---------- Comparación pareada ----------
def sign_test(wins, losses):
    n = wins + losses
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(wins, losses) + 1)) / 2 ** n)


def paired(g, better, other, measure):
    keys = sorted(set(g[better]) & set(g[other]))
    combos = sum(abs(g[better][k][f"{measure}_err"]) < abs(g[other][k][f"{measure}_err"]) for k in keys)
    wins = losses = 0
    for rep in sorted({k[0] for k in keys}):
        ks = [k for k in keys if k[0] == rep]
        a = np.mean([abs(g[better][k][f"{measure}_err"]) for k in ks])
        b = np.mean([abs(g[other][k][f"{measure}_err"]) for k in ks])
        wins += a < b; losses += a > b
    return {"combinaciones": f"{combos}/{len(keys)}", "replicas": f"{wins}/{wins + losses}",
            "p": sign_test(wins, losses)}


def bland_altman(pairs):
    d = np.array([e - y for e, y in pairs]); bias = float(d.mean()); sd = float(d.std(ddof=1))
    return {"n": len(pairs), "sesgo": bias, "loa_inf": bias - 1.96 * sd, "loa_sup": bias + 1.96 * sd}


# ---------- Ruta C a una profundidad supuesta ----------
def c_rows(rows):
    return sorted((r for r in rows if r["method"] == "C"),
                  key=lambda r: (int(r["replicate_id"][1:]), int(r["position_mm"]), r["repetition"]))


def measure_at(row, air, port, z_mm):
    """C con el plano de la réplica a z mm de la cara interna del vidrio."""
    plane = make_measurement_plane((0.0, 0.0, port.interface_distance_mm + port.glass_thickness_mm + z_mm),
                                   (0.0, 0.0, 1.0), source="z_desde_cara_interna_del_vidrio",
                                   plane_id=f"z-{z_mm:g}-mm")
    points = {p: (float(row[f"{p}_x_px"]), float(row[f"{p}_y_px"])) for p in ("p1", "p2", "p3", "p4")}
    res = measure_c(row["image_id"], points, air, port, plane, replica_id=row["replicate_id"],
                    repetition=row["repetition"], image_shape=(3072, 4096), longitudinal_axis_px=(1.0, 0.0))
    return float(res.total_length_mm), float(res.body_depth_mm)


def sensitivity(rows, air, port):
    scenarios = {"d = 184 mm (-20 %)": replace(port, interface_distance_mm=184.0),
                 "d = 276 mm (+20 %)": replace(port, interface_distance_mm=276.0),
                 "mu_w = 1,323 (-0,01)": replace(port, n_water=1.323),
                 "mu_w = 1,343 (+0,01)": replace(port, n_water=1.343)}
    detail = []
    for r in c_rows(rows):
        z = float(r["position_mm"]); base, _ = measure_at(r, air, port, z)
        for name, p in scenarios.items():
            lt, _ = measure_at(r, air, p, z)
            detail.append({"escenario": name, "image_id": r["image_id"], "lt_base_mm": base,
                           "lt_variante_mm": lt, "delta_mm": lt - base, "delta_pct": (lt - base) / base * 100})
    summary = {n: {"delta_mm": float(np.mean([d["delta_mm"] for d in detail if d["escenario"] == n])),
                   "delta_pct": float(np.mean([d["delta_pct"] for d in detail if d["escenario"] == n])),
                   "max_abs_mm": float(max(abs(d["delta_mm"]) for d in detail if d["escenario"] == n))}
               for n in scenarios}
    return summary, detail


def interval(rows, air, port):
    grid = []
    for r in c_rows(rows):
        for z in range(0, 301, 10):
            lt, pc = measure_at(r, air, port, float(z))
            grid.append({"image_id": r["image_id"], "replicate_id": r["replicate_id"],
                         "position_mm": int(r["position_mm"]), "repetition": r["repetition"],
                         "z_mm": z, "lt_mm": lt, "pc_mm": pc})
    increasing = sum(np.all(np.diff([g["lt_mm"] for g in grid if g["image_id"] == i]) > 0)
                     for i in {g["image_id"] for g in grid})
    D = lambda z: port.interface_distance_mm + port.glass_thickness_mm / port.n_glass + z / port.n_water
    windows = {"0-30 cm": lambda z0: (0.0, 300.0),
               "+-3 cm": lambda z0: (max(0.0, z0 - 30), min(300.0, z0 + 30)),
               "+-1 cm": lambda z0: (max(0.0, z0 - 10), min(300.0, z0 + 10))}
    detail = []
    for r in c_rows(rows):
        z0 = float(r["position_mm"]); ref = float(r["lt_reference_mm"])
        for name, lim in windows.items():
            lo, hi = lim(z0)
            a, _ = measure_at(r, air, port, lo); b, _ = measure_at(r, air, port, hi)
            lower, upper = min(a, b), max(a, b)
            detail.append({"escenario": name, "image_id": r["image_id"], "position_mm": int(z0),
                           "z_inf_mm": lo, "z_sup_mm": hi, "lt_inf_mm": lower, "lt_sup_mm": upper,
                           "lt_ref_mm": ref, "cubre": lower <= ref <= upper,
                           "ancho_num_pct": (upper - lower) / ref * 100,
                           "ancho_pred_pct": (D(hi) - D(lo)) / D(z0) * 100})
    summary = {}
    for name in windows:
        sel = [d for d in detail if d["escenario"] == name]
        summary[name] = {"cobertura": sum(d["cubre"] for d in sel) / len(sel),
                         "cubiertas": f"{sum(d['cubre'] for d in sel)}/{len(sel)}",
                         "razon_pred_num": float(np.mean([d["ancho_pred_pct"] / d["ancho_num_pct"] for d in sel])),
                         "por_posicion": {p: (float(np.mean([d["ancho_num_pct"] for d in sel if d["position_mm"] == p])),
                                              float(np.mean([d["ancho_pred_pct"] for d in sel if d["position_mm"] == p])))
                                          for p in POSITIONS}}
    return {"lz_creciente": f"{increasing}/{len({g['image_id'] for g in grid})}", "ventanas": summary}, grid, detail


# ---------- Figuras ----------
def comma(v, _pos=None):
    return f"{v:g}".replace(".", ",")


def configure():
    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 10,
                         "axes.labelsize": 10, "legend.fontsize": 8, "xtick.labelsize": 9,
                         "ytick.labelsize": 9, "pdf.fonttype": 42, "ps.fonttype": 42})


def figure_bland_altman(g_c, ba, path):
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.6))
    for ax, m, label in zip(axes, ("lt", "pc"), ("LT", "PC")):
        est = np.array([v[f"{m}_mm"] for v in g_c.values()]); ref = np.array([v[f"{m}_ref"] for v in g_c.values()])
        s = ba[m]
        ax.scatter((est + ref) / 2, est - ref, s=24, color=COLOR_C, alpha=0.85)
        ax.axhline(s["sesgo"], color="#222222", linewidth=1.0, label="Sesgo")
        ax.axhline(s["loa_inf"], color="#777777", linewidth=0.9, linestyle="--", label="Límites de acuerdo")
        ax.axhline(s["loa_sup"], color="#777777", linewidth=0.9, linestyle="--")
        ax.set_xlabel(f"Promedio de {label}: C y calibre (mm)")
        ax.set_ylabel(f"C − calibre en {label} (mm)")
        ax.xaxis.set_major_formatter(FuncFormatter(comma)); ax.yaxis.set_major_formatter(FuncFormatter(comma))
        ax.grid(color="#E3E3E3", linewidth=0.5)
    handles, labels = axes[1].get_legend_handles_labels()
    fig.subplots_adjust(left=0.10, right=0.98, top=0.96, bottom=0.25, wspace=0.32)
    fig.legend(handles, labels, ncol=2, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 0.02))
    fig.savefig(path); plt.close(fig)


def figure_lz(grid, rows, path):
    refs = {r["image_id"]: r for r in c_rows(rows)}
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.6))
    for ax, image_id in zip(axes, ("R1-REP1-50.jpg", "R6-REP1-230.jpg")):
        recs = sorted((g for g in grid if g["image_id"] == image_id), key=lambda g: g["z_mm"])
        z0 = float(refs[image_id]["position_mm"]); ref = float(refs[image_id]["lt_reference_mm"])
        ax.axvspan(max(0, z0 - 30), min(300, z0 + 30), color="#A9CCE3", alpha=0.35, label="Ventana ±3 cm")
        ax.axvspan(max(0, z0 - 10), min(300, z0 + 10), color="#F9E79F", alpha=0.65, label="Ventana ±1 cm")
        ax.plot([g["z_mm"] for g in recs], [g["lt_mm"] for g in recs], color=COLOR_C, linewidth=1.5, label="L(z)")
        ax.axhline(ref, color="#333333", linestyle="--", linewidth=1.0, label="LT de calibre")
        ax.axvline(z0, color="#7D3C98", linestyle=":", linewidth=1.2, label="z real")
        ax.set_xlabel("z desde la cara interna del vidrio (mm)"); ax.set_ylabel("LT estimada (mm)")
        ax.set_title(image_id.replace(".jpg", ""))
        ax.xaxis.set_major_formatter(FuncFormatter(comma)); ax.yaxis.set_major_formatter(FuncFormatter(comma))
        ax.grid(color="#E3E3E3", linewidth=0.5)
    handles, labels = axes[1].get_legend_handles_labels()
    fig.subplots_adjust(left=0.10, right=0.98, top=0.90, bottom=0.27, wspace=0.26)
    fig.legend(handles, labels, ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 0.01))
    fig.savefig(path); plt.close(fig)


def write_csv(path, records):
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(records[0])); w.writeheader(); w.writerows(records)


# ---------- Principal ----------
def main():
    rows = read_rows()
    assert len(rows) == 288, len(rows)
    g, t44, t45 = tables(rows)
    common = common_images(rows)
    _, t44c, t45c = tables(rows, common)
    max_shift = max([abs(t44[m][k] - t44c[m][k]) for m in METHODS for k in t44[m] if k != "n"]
                    + [abs(t45[p][m] - t45c[p][m]) for p in POSITIONS for m in METHODS])
    capture = {m: per_capture(rows, m) for m in METHODS}
    sep = [0, 6, 12, 18]
    slopes = {"A": float(np.polyfit(sep, [t45[p]["A"] for p in POSITIONS], 1)[0]),
              "B-C": float(np.polyfit(sep, [t45[p]["B"] - t45[p]["C"] for p in POSITIONS], 1)[0])}
    pairs = {f"{a} vs {b} ({m.upper()})": paired(g, a, b, m)
             for m in ("lt", "pc") for a, b in (("C", "A"), ("C", "A′"), ("C", "B"), ("B", "A"), ("B", "A′"))}
    ba = {meth: {m: bland_altman([(v[f"{m}_mm"], v[f"{m}_ref"]) for v in g[meth].values()]) for m in ("lt", "pc")}
          for meth in ("B", "C")}
    ba_capturas_c = {m: bland_altman([(float(r[f"{m}_mm"]), float(r[f"{m}_reference_mm"]))
                                      for r in rows if r["method"] == "C"]) for m in ("lt", "pc")}

    air = load_air_calibration(CALIB / "calibration_C_air.yaml")
    port = load_manual_flat_port(CALIB / "flat_port.yaml")
    nominal = [abs(measure_at(r, air, port, float(r["position_mm"]))[0] - float(r["lt_mm"])) for r in c_rows(rows)]
    sens, sens_detail = sensitivity(rows, air, port)
    lz, grid, intervals = interval(rows, air, port)

    DERIV.mkdir(parents=True, exist_ok=True)
    write_csv(DERIV / "sensibilidad_c.csv", sens_detail)
    write_csv(DERIV / "L_z.csv", grid)
    write_csv(DERIV / "intervalos_L_z.csv", intervals)
    configure()
    figure_bland_altman(g["C"], ba["C"], FIG / "fig4_bland_altman_c.pdf")
    figure_lz(grid, rows, FIG / "fig4_L_z_ejemplos.pdf")

    summary = {"tabla_4_4": t44, "tabla_4_4_por_captura": capture, "tabla_4_5": t45, "pendientes_mm_por_cm": slopes,
               "interseccion_70": {"imagenes": len(common), "max_cambio": max_shift},
               "comparacion_pareada": pairs, "bland_altman_combinaciones": ba, "bland_altman_capturas_C": ba_capturas_c,
               "C_en_posicion_nominal": {"iguales_a_0_01_mm": sum(d < 0.01 for d in nominal), "n": len(nominal),
                                         "max_dif_mm": max(nominal)},
               "tabla_4_3_sensibilidad": sens, "tabla_4_6_intervalo": lz}
    (DERIV / "resumen_capitulo4.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")

    f = lambda v: f"{v:+.2f}" if v < 0 else f"{v:.2f}"
    print("Tabla 11 - sensibilidad de C (cambio medio de LT)")
    for k, v in sens.items():
        print(f"  {k:22s} {v['delta_mm']:+7.2f} mm {v['delta_pct']:+7.2f} %  (máx. {v['max_abs_mm']:.2f} mm)")
    print("Tabla 12 - sesgo LT, MAE LT, MAPE LT, sesgo PC, MAE PC, MAPE PC | MAE LT y PC por captura")
    for m in METHODS:
        t, c = t44[m], capture[m]
        print(f"  {m:3s} n={t['n']}  " + "  ".join(f(t[k]) for k in ("sesgo_lt", "mae_lt", "mape_lt", "sesgo_pc", "mae_pc", "mape_pc"))
              + f"  | {c['mae_lt']:.2f} {c['mae_pc']:.2f} (n={c['n']})")
    print("Tabla 13 - MAE de LT por posición (A, A′, B, C, B-C)")
    for p in POSITIONS:
        print(f"  {p // 10:2d} cm  " + "  ".join(f"{t45[p][m]:.2f}" for m in METHODS) + f"  {t45[p]['B'] - t45[p]['C']:+.2f}")
    print(f"  pendientes: A {slopes['A']:+.2f} mm/cm; B-C {slopes['B-C']:+.3f} mm/cm")
    print(f"Intersección de {len(common)} imágenes: cambio máximo {max_shift:.4f}")
    print("Comparación pareada (gana el primero): combinaciones, réplicas, p de la prueba de signos")
    for k, v in pairs.items():
        print(f"  {k:14s} {v['combinaciones']:>6s}  {v['replicas']:>4s}  p = {v['p']:.3f}")
    for meth in ("C", "B"):
        for m in ("lt", "pc"):
            s = ba[meth][m]
            print(f"Bland-Altman {meth} {m.upper()} (24 comb.): sesgo {s['sesgo']:+.2f}; LoA {s['loa_inf']:+.2f} / {s['loa_sup']:+.2f} mm")
    for m in ("lt", "pc"):
        s = ba_capturas_c[m]
        print(f"Bland-Altman C {m.upper()} (72 capturas): LoA {s['loa_inf']:+.2f} / {s['loa_sup']:+.2f} mm")
    print(f"C recalculado en la posición nominal: {sum(d < 0.01 for d in nominal)}/{len(nominal)} a menos de 0,01 mm; "
          f"diferencia máxima {max(nominal):.2f} mm")
    print(f"Tabla 14 - L(z) creciente en {lz['lz_creciente']} capturas; ancho numérico (predicción) por posición")
    for name, s in lz["ventanas"].items():
        print(f"  {name:8s} " + "  ".join(f"{a:.1f} ({b:.1f})" for a, b in s["por_posicion"].values())
              + f"  cobertura {s['cobertura']:.2f} ({s['cubiertas']}); razón pred/num {s['razon_pred_num']:.3f}")


if __name__ == "__main__":
    main()
