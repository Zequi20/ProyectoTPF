#!/usr/bin/env python3
"""Renderiza los fragmentos de ``adjuntos/tablas`` como imagenes PNG."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from generar_adjuntos import OUTPUT, ROOT, TABLES, TABLE_OUTPUT, filename_prefix, main as generar_adjuntos


IMAGE_OUTPUT = OUTPUT / "tablas_imagen"
TEMP_ROOT = ROOT / "tmp/pdfs/tablas"
RENDER_DPI = 220


def latex_number(number: str) -> str:
    if number.isdigit():
        return f"\\setcounter{{table}}{{{int(number) - 1}}}"
    return f"\\renewcommand{{\\thetable}}{{{number[0]}\\arabic{{table}}}}\n\\setcounter{{table}}{{{int(number[1:]) - 1}}}"


def document_source(table_path: Path, number: str) -> str:
    return rf"""\documentclass[10pt,letterpaper]{{article}}
\usepackage[utf8]{{inputenc}}
\DeclareUnicodeCharacter{{1EBD}}{{\~e}}
\DeclareUnicodeCharacter{{1EF9}}{{\~y}}
\usepackage[T1]{{fontenc}}
\usepackage{{lmodern}}
\usepackage[english,spanish,es-tabla,es-lcroman,es-nodecimaldot,es-noshorthands]{{babel}}
\usepackage{{csquotes}}
\usepackage[letterpaper,landscape,margin=0.45in]{{geometry}}
\usepackage{{setspace}}
\usepackage{{amsmath,amssymb,bm}}
\usepackage{{etoolbox}}
\usepackage{{siunitx}}
\sisetup{{output-decimal-marker={{,}},group-separator={{\,}},per-mode=symbol}}
\usepackage{{booktabs,longtable,array,multirow,makecell,tabularx}}
\usepackage{{pdflscape}}
\usepackage{{caption}}
\captionsetup{{labelfont=bf,textfont=it,labelsep=newline,justification=raggedright,singlelinecheck=false}}
\usepackage{{float}}
\usepackage{{xcolor}}
\newcommand{{\Aprime}}{{A$'$}}
\newcommand{{\IL}}{{I_L}}
\AtBeginEnvironment{{longtable}}{{\setstretch{{1}}}}
\usepackage{{xr}}
\externaldocument{{main}}
\usepackage[backend=biber,style=apa,language=spanish,natbib=true]{{biblatex}}
\DeclareLanguageMapping{{spanish}}{{spanish-apa}}
\addbibresource{{referencias.bib}}
\begin{{document}}
\pagestyle{{empty}}
\setstretch{{1}}
{latex_number(number)}
\input{{{table_path.relative_to(ROOT).as_posix()}}}
\end{{document}}
"""


def run(command: list[str], *, label: str) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode:
        tail = "\n".join(result.stdout.splitlines()[-80:])
        raise RuntimeError(f"Fallo al {label}:\n{tail}")


def combine_pages(page_paths: list[Path], destination: Path) -> None:
    pages = [Image.open(path).convert("RGB") for path in page_paths]
    gap = 24
    width = max(page.width for page in pages)
    height = sum(page.height for page in pages) + gap * (len(pages) - 1)
    combined = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(combined)
    y = 0
    for index, page in enumerate(pages):
        x = (width - page.width) // 2
        combined.paste(page, (x, y))
        y += page.height
        if index + 1 < len(pages):
            separator_y = y + gap // 2
            draw.line((0, separator_y, width, separator_y), fill=(205, 205, 205), width=2)
            y += gap
    destination.parent.mkdir(parents=True, exist_ok=True)
    combined.save(destination, format="PNG", optimize=True, dpi=(RENDER_DPI, RENDER_DPI))
    for page in pages:
        page.close()


def render_table(label: str, number: str, slug: str) -> Path:
    base = f"{filename_prefix('tabla', number)}_{slug}"
    source_table = TABLE_OUTPUT / f"{base}.tex"
    build_dir = TEMP_ROOT / base
    build_dir.mkdir(parents=True, exist_ok=True)
    render_source = build_dir / f"{base}_render.tex"
    render_source.write_text(document_source(source_table, number), encoding="utf-8")

    run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            f"-outdir={build_dir}",
            str(render_source),
        ],
        label=f"compilar {label}",
    )

    rendered_pdf = build_dir / f"{base}_render.pdf"
    cropped_pdf = build_dir / f"{base}_recortada.pdf"
    run(["pdfcrop", "--margins", "10", str(rendered_pdf), str(cropped_pdf)], label=f"recortar {label}")

    page_prefix = build_dir / "pagina"
    run(
        ["pdftoppm", "-r", str(RENDER_DPI), "-png", str(cropped_pdf), str(page_prefix)],
        label=f"convertir {label} a PNG",
    )
    page_paths = sorted(build_dir.glob("pagina-*.png"), key=lambda path: int(path.stem.rsplit("-", 1)[1]))
    if not page_paths:
        raise RuntimeError(f"No se generaron paginas para {label}")

    destination = IMAGE_OUTPUT / f"{base}.png"
    combine_pages(page_paths, destination)
    return destination


def main() -> None:
    generar_adjuntos()
    IMAGE_OUTPUT.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)

    outputs = []
    try:
        for label, metadata in TABLES.items():
            output = render_table(label, metadata.number, metadata.slug)
            outputs.append(output)
            print(f"Renderizada {label}: {output.relative_to(ROOT)}")
    finally:
        if TEMP_ROOT.is_dir():
            shutil.rmtree(TEMP_ROOT)
        pdf_root = ROOT / "tmp/pdfs"
        if pdf_root.is_dir() and not any(pdf_root.iterdir()):
            pdf_root.rmdir()
        temp_root = ROOT / "tmp"
        if temp_root.is_dir() and not any(temp_root.iterdir()):
            temp_root.rmdir()

    if len(outputs) != len(TABLES):
        raise RuntimeError(f"Se esperaban {len(TABLES)} imagenes y se generaron {len(outputs)}")

    # Actualiza el indice y el README para enlazar las imagenes recien creadas.
    generar_adjuntos()
    print(f"Imagenes generadas: {len(outputs)} en {IMAGE_OUTPUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
