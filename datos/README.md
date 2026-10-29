# Datos del experimento

Conjunto de datos de la tesis *Estimación morfométrica monocular de peces a través de una
interfaz aire–vidrio–agua*. Seis réplicas rígidas de PLA (R1–R6), fotografiadas a cuatro
distancias nominales del vidrio (50, 110, 170 y 230 mm) con tres capturas por condición.
El código que procesó las imágenes es Fishmeter, etiqueta `v1.0-tesis` de
<https://github.com/Zequi20/FishmeterTPF>.

| Carpeta o archivo | Contenido |
|---|---|
| `imagenes/` | Las 72 fotografías originales (JPG, 4096 × 3072 px, Realme C71). Nombre: `R<réplica>-REP<repetición>-<distancia al vidrio en mm>.jpg`. |
| `calibraciones/calibration_B.yaml` | Perfil `B-effective`: calibración pinhole efectiva con el damero sumergido. |
| `calibraciones/calibration_C_air.yaml` | Perfil `C-air`: calibración de la cámara en aire. |
| `calibraciones/flat_port.yaml` | Parámetros del puerto plano que usa C (d = 230 mm, t_g = 4 mm, índices). |
| `calibraciones/rail_reference_B.yaml` | Referencia geométrica del riel que usa B (cero del riel en la posición de 50 mm). |
| `referencias/replicas.csv` | Las tres lecturas de calibre de LT y PC de cada réplica, en mm. |
| `resultados_json/` | Un JSON por imagen y método (284), con los puntos marcados en píxeles, los parámetros de la ruta y sus advertencias. Faltan A y A′ de `R2-REP2-170` y `R3-REP2-50`, en las que no se detectó el ArUco. |
| `resultados_json/re_run_B/` | Los 72 JSON de B recalculados con la lectura del riel (z − 50 mm) por `analysis/re_run_b.py`, y el informe de verificación de ese recálculo. |
| `derivados/` | Salidas de `analysis/reproducir_capitulo4.py`: L(z) por captura, intervalos y cobertura, sensibilidad de C y resumen de las cifras del Capítulo 4. |
| `SHA256SUMS` | Huellas SHA-256 de todos los archivos de esta carpeta. |

La tabla maestra (288 registros, uno por imagen y método) está en
`../anexos/csv-maestro-re-run.csv`; `../anexos/csv_maestro_morfometrico.csv` es la versión
anterior al recálculo de B.

## Notas sobre los datos

- **B y el marco del riel.** Los JSON de B en `resultados_json/` son los del cálculo
  preliminar, que recibió la distancia nominal al vidrio en lugar de la lectura del riel. Los
  valores de B de la tesis son los de `re_run_B/`, que son los que recoge
  `csv-maestro-re-run.csv`.
- **Desplazamiento del plano de simetría.** El plano de simetría de cada réplica quedaba
  10 mm corrido respecto del apoyo del carrito. Se compensó físicamente en el montaje,
  corriendo el carrito 10 mm; por eso el procesamiento usa un desplazamiento de réplica de 0 mm.
- **PC de R1 y R2.** Las lecturas de profundidad corporal de R1 y R2 se anotaron con un cero
  de más (450 por 45 mm; 280/270 por 28/27 mm). Están corregidas en `replicas.csv` y en los
  CSV maestros.
- **Rutas locales.** Algunos YAML y JSON conservan rutas absolutas del equipo en que se
  generaron. No se editaron, porque sus huellas quedaron registradas en la tabla maestra.

## Reproducción del Capítulo 4

Desde la raíz del proyecto, con Fishmeter `v1.0-tesis` instalado (`pip install -e .` en su
repositorio) o con la variable `FISHMETER_SRC` apuntando a su carpeta `src/`:

```bash
(cd datos && sha256sum -c SHA256SUMS)   # opcional: integridad de los datos
python analysis/reproducir_capitulo4.py  # Tablas 11–14, valores de la Tabla 15, pruebas de
                                         # signos, Bland–Altman, Figuras 19 (L(z)) y 20 (Bland–Altman)
python analysis/make_figures.py          # Figuras 15–18 y 21
python analysis/tabla_maestra.py         # Tabla del Anexo F
```

`make_figures.py` lee `datos/derivados/intervalos_L_z.csv`, por lo que debe ejecutarse
después de `reproducir_capitulo4.py`.

`analysis/re_run_b.py` generó `../anexos/csv-maestro-re-run.csv` y `resultados_json/re_run_B/`
a partir de `../anexos/csv_maestro_morfometrico.csv` y los JSON de B preliminares. No hace
falta ejecutarlo para reproducir el capítulo; no sobrescribe salidas existentes, así que para
comprobarlo hay que indicar otras rutas con `--output-csv` y `--output-dir`. El CSV que produce
es idéntico al publicado y los JSON solo difieren en el campo `re_run.script`.
