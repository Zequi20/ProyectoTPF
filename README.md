# Tesis de Ezequiel — versión corregida (v2, 13/10/2026)

Proyecto LaTeX completo de la tesis con las correcciones de las dos revisiones integradas.

## Compilar
    latexmk -pdf main.tex        # pdflatex + biber (requiere biblatex-apa, babel-spanish, tikz, tcolorbox, siunitx, glossaries)

## Estructura
- `main.tex`               preámbulo y orden de los capítulos
- `preliminares/`          portada, ficha, advertencia, hoja de aprobación, dedicatoria, agradecimientos, acrónimos, resumen, abstract, datos
- `capitulos/1-5*.tex`     los cinco capítulos
- `anexos/anexos.tex`      anexos A–H (H = registro de cambios, Art. 17)
- `referencias.bib`        bibliografía corregida (APA 7)
- `figuras/originales/`    figuras extraídas del libro anterior
- `figuras/fig4_*.pdf`     figuras del Capítulo 4 generadas por `analysis/make_figures.py`
- `figuras/tikz/`          versiones PNG de los diagramas TikZ (para el DOCX)
- `analysis/make_figures.py`  regenera las figuras del Capítulo 4 (reemplazar los valores por lectura del CSV maestro)
- `build_docx/`            fuente intermedia para generar el DOCX con pandoc

## Pendientes
Los recuadros naranjas "PENDIENTE Pn" y las marcas `[...]` en naranja señalan lo que requiere datos
(CSV maestro, imágenes, nuevas mediciones). Están listados en el Anexo H. Deben resolverse y
eliminarse antes de la entrega: buscar `\pendiente{` y `\pend{` en los .tex.
