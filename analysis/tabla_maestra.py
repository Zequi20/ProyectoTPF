"""Genera anexos/tabla_maestra.tex (Anexo de la tabla maestra) a partir del CSV maestro.

Una fila por imagen: referencias de calibre y estimaciones de LT y PC de cada método.
Usa solo la biblioteca estándar.
"""
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "anexos" / "csv-maestro-re-run.csv"
OUT = ROOT / "anexos" / "tabla_maestra.tex"
METHODS = ["A", "A′", "B", "C"]


def num(value):
    return f"{float(value):.1f}".replace(".", ",") if value else "---"


rows = {}
with open(CSV, encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        rows.setdefault(r["image_id"], {})[r["method"]] = r


def order(image_id):
    rep, repetition, pos = image_id.removesuffix(".jpg").split("-")
    return rep, int(pos), repetition


lines = []
for image_id in sorted(rows, key=order):
    by_method = rows[image_id]
    ref = by_method["C"]
    cells = [f"\\texttt{{{image_id.removesuffix('.jpg')}}}", num(ref["lt_reference_mm"])]
    cells += [num(by_method[m]["lt_mm"]) for m in METHODS]
    cells += [num(ref["pc_reference_mm"])]
    cells += [num(by_method[m]["pc_mm"]) for m in METHODS]
    lines.append(" & ".join(cells) + " \\\\")

sha = hashlib.sha256(CSV.read_bytes()).hexdigest()
header = (" & \\multicolumn{5}{c}{Longitud total (mm)} & \\multicolumn{5}{c}{Profundidad corporal (mm)} \\\\\n"
          "\\cmidrule(lr){2-6}\\cmidrule(l){7-11}\n"
          "Imagen & Ref. & A & \\Aprime & B & C & Ref. & A & \\Aprime & B & C \\\\\n")
OUT.write_text(
    "% Generado por analysis/tabla_maestra.py; no editar a mano.\n"
    f"% CSV: {CSV.name}, SHA-256 {sha}\n"
    "\\newcommand{\\MaestraSHA}{" + sha + "}\n"
    "\\begin{footnotesize}\n"
    "\\setlength{\\tabcolsep}{4pt}\n"
    "\\begin{longtable}{@{}lrrrrrrrrrr@{}}\n"
    "\\caption{Tabla maestra: referencias de calibre y estimaciones por imagen y método.}\n"
    "\\label{tab:maestra}\\\\\n"
    "\\toprule\n" + header + "\\midrule\n\\endfirsthead\n"
    "\\toprule\n" + header + "\\midrule\n\\endhead\n"
    "\\bottomrule\n\\endfoot\n"
    + "\n".join(lines) + "\n"
    "\\end{longtable}\n"
    "\\end{footnotesize}\n",
    encoding="utf-8",
)
print(f"{OUT.relative_to(ROOT)}: {len(lines)} filas; SHA-256 {sha}")
