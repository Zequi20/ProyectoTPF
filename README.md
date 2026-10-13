# Tesis de Ezequiel: proyecto LaTeX y datos del experimento

Proyecto LaTeX de la tesis *Estimación morfométrica monocular de peces a través de una
interfaz aire–vidrio–agua* y datos del experimento con los scripts que regeneran el Capítulo 4.
El código de la aplicación Fishmeter está en <https://github.com/Zequi20/FishmeterTPF>
(etiqueta `v1.0-tesis`).

## Compilar
    latexmk -pdf main.tex        # pdflatex + biber (requiere biblatex-apa, babel-spanish, tikz, tcolorbox, siunitx, glossaries)

## Estructura
- `main.tex`               preámbulo y orden de los capítulos
- `preliminares/`          portada, ficha, advertencia, hoja de aprobación, dedicatoria, agradecimientos, acrónimos, resumen, abstract, datos
- `capitulos/1-5*.tex`     los cinco capítulos
- `anexos/anexos.tex`      anexos A–G
- `anexos/*.csv`           tabla maestra del experimento (`csv-maestro-re-run.csv`) y su versión anterior al recálculo de B
- `referencias.bib`        bibliografía (APA 7)
- `figuras/`               figuras del libro; las del Capítulo 4 se generan con los scripts de `analysis/`
- `datos/`                 imágenes, calibraciones, referencias de calibre y resultados por imagen (ver `datos/README.md`)
- `analysis/`              scripts que regeneran las tablas y figuras del Capítulo 4 y la tabla del Anexo F
- `build_docx/`            fuente intermedia para generar el DOCX con pandoc

## Reproducir el Capítulo 4
Con Fishmeter `v1.0-tesis` instalado (o `FISHMETER_SRC` apuntando a su carpeta `src/`):

    python analysis/reproducir_capitulo4.py
    python analysis/make_figures.py
    python analysis/tabla_maestra.py

`datos/README.md` describe cada archivo, las convenciones de los datos y qué tabla o figura produce cada script.
