# Tarea: obtener desde Fishmeter los datos que faltan en la tesis

Trabajás dentro del repositorio **Fishmeter** (`~/Documentos/repos/Fishmeter`, paquete `src/fish_morphometry`). La tesis LaTeX que usa este software está en `~/Documentos/tesis_ezequiel_v2_latex/tesis_v2`. Ahí, los recuadros `\pendiente{...}` y las marcas `\pend{...}` señalan datos que faltan. Tu trabajo es obtener, a partir del código y los datos de Fishmeter, los datos de los pendientes listados abajo y entregarlos en **un único archivo Markdown** con un texto listo para pegar en la tesis.

No edites la tesis. Solo producís el informe y los archivos que lo respaldan.

## Entregables

Todo va en `outputs/tesis_pendientes/` (la carpeta `outputs/` no está versionada):

- `RESPUESTAS_PENDIENTES.md`: el informe, con el formato que se describe al final.
- `scripts/`: cada script que uses para calcular algo, ejecutable desde la raíz del repo, para que cualquier cifra se pueda regenerar.
- `figuras/`: las figuras pedidas, en PDF vectorial (y PNG a 200 dpi si incluyen una fotografía).
- `datos/`: los CSV que generes (por ejemplo, `L_z.csv`).

## Reglas

1. **No inventes valores.** Cada cifra tiene que salir de un archivo, de una ejecución del código o de un cálculo con script. Si algo no se puede obtener, escribí «No resoluble desde el repositorio» y explicá qué falta.
2. **Citá la fuente de cada dato** con `archivo:línea`, el comando ejecutado o el script de `scripts/` que lo produce.
3. **No modifiques código, configuraciones ni datos existentes.** Si para un cálculo necesitás cambiar un parámetro (por ejemplo, `d` o `μ_w`), hacelo en memoria o sobre una copia dentro de `outputs/tesis_pendientes/`.
4. **No hagas `git commit`, `git tag` ni `git push`.** Si un pendiente requiere una acción en el repositorio (crear la etiqueta, publicar datos), describí los pasos exactos y no los ejecutes.
5. **Si no encontrás un insumo** (imágenes, YAML de calibración, anotaciones), buscalo siguiendo las rutas registradas en los JSON de `results/` y en el CSV maestro. Si aun así no aparece, detenete y preguntale la ruta al usuario. No lo reconstruyas.
6. **Convenciones de la tesis para los textos LaTeX:**
   - Coma decimal: `1,22~mm` en el texto y `0{,}031` dentro de modo matemático.
   - Unidades con `~`.
   - Macro `\Aprime{}` para el método A′ y macro `\IL` para el intervalo $I_L$.
   - Tiempo pasado para lo realizado.
   - Sin adjetivos de autoelogio.
7. **Figuras:**
   - Matplotlib, `DejaVu Sans` de 10 pt, sin título dentro de la figura (el título va en el `\caption`).
   - Etiquetas en español y coma decimal en los ejes.
   - Colores por método iguales a los de las figuras existentes: A `#C0392B`, A′ `#E67E22`, B `#2E86C1`, C `#1E8449`.
   - Tamaño aproximado de 6,4 × 3,6 in.

## Contexto mínimo

- **Diseño:** 6 réplicas rígidas de PLA (R1–R6), 4 posiciones nominales de la réplica respecto de la cara interna del vidrio (5, 11, 17 y 23 cm; en los nombres de archivo, `50`, `110`, `170` y `230`) y 3 repeticiones técnicas por posición. Total: 72 imágenes, 4 métodos y 288 registros. La unidad experimental es la réplica (n = 6) y hay 24 combinaciones réplica–profundidad.
- **Métodos:**
  - **A:** escala de un ArUco fijo en el vidrio.
  - **A′:** homografía de un ArUco coplanar con la réplica.
  - **B:** pinhole efectivo calibrado bajo el agua, perfil `B-effective`, con un plano de referencia obtenido del riel (`rail_reference_B.yaml`).
  - **C:** modelo refractivo de puerto plano, perfil `C-air`, con $d = 230$ mm, $t_g = 4{,}0$ mm, $μ_a = 1{,}000$, $μ_g = 1{,}500$ y $μ_w = 1{,}333$.
- **Medidas:** LT es la proyección de p1→p2 sobre el eje longitudinal. PC es la proyección de p3→p4 sobre la normal al eje.
- **Agregación usada en la tesis:**
  1. Se promedian las 3 repeticiones de cada combinación réplica–profundidad.
  2. Sobre las 24 combinaciones se calculan el sesgo, el MAE y el MAPE.
  3. La inferencia es una prueba de signos exacta de dos colas con la réplica como unidad: para cada réplica se promedia el error absoluto sobre las 4 posiciones y se comparan C frente a cada método (n = 6).
- **Exclusiones:** A y A′ no tienen valor en `R2-REP2-170.jpg` ni en `R3-REP2-50.jpg` (ArUco no detectado). Por eso tienen 70 imágenes con valor, mientras que B y C tienen 72.
- **Profundidad desconocida:** $I_L = [\min_z L(z), \max_z L(z)]$ sobre el rango admisible de $z$, que es la distancia de la cara interna del vidrio al plano de medición de la réplica, entre 0 y 300 mm. La aproximación de primer orden usada en la tesis es $D(z) = d + t_g/μ_g + z/μ_w$, con $L(z) ∝ D(z)$.

### Insumos conocidos

Verificalos antes de usarlos:

- **CSV maestro:** `~/Documentos/csv_maestro_morfometrico.csv`, fuera del repo. Tiene 288 filas y columnas como `replicate_id`, `position_mm`, `repetition`, `image_id`, `method` (con los valores `A`, `A′`, `B` y `C`), `lt_mm`, `pc_mm`, `lt_reference_mm`, `pc_reference_mm`, los errores con signo y absolutos, `aruco_detected`, `exclusion_reason`, `p1_x_px`…`p4_y_px`, etc.
- **Versión en Excel:** `outputs/fishmeter-resultados-maestro/resultados_morfometricos_maestro.xlsx`. Confirmá si coincide con el CSV.
- **Resultados por imagen:** `results/*.json`, unos 285 archivos ignorados por git.
- **Lecturas de calibre:** `~/Documentos/datos-fisicos.csv`.
- **Lo que no está en el repo:** `data/raw/`, `data/annotations/`, `data/references/` y `calibrations/*` están vacíos o ignorados. Las 72 imágenes, los JSON de puntos y los YAML de calibración pueden estar en otra ruta.
- **Código relevante:** `src/fish_morphometry/methods/c.py` (`measure_c`, línea ~120) y `src/fish_morphometry/validation/c_validation.py` (`sensitivity_c`, línea ~331).

### Cifras que la tesis informa hoy

Sirven para la verificación del paso 0.

**Tabla 4.2** (24 combinaciones, repeticiones promediadas):

| Método | n | Sesgo LT | MAE LT | MAPE LT % | Sesgo PC | MAE PC | MAPE PC % |
|---|---|---|---|---|---|---|---|
| A | 24 | −37,43 | 37,43 | 25,68 | −9,07 | 9,07 | 25,25 |
| A′ | 24 | +3,29 | 3,29 | 2,28 | +0,95 | 1,03 | 2,78 |
| B | 24 | +16,32 | 16,32 | 11,24 | +3,68 | 3,68 | 9,96 |
| C | 24 | +1,07 | 1,22 | 0,88 | +0,29 | 0,56 | 1,62 |

**Tabla 4.3** (MAE de LT por posición, en mm):

| Posición (cm) | A | A′ | B | C | B−C |
|---|---|---|---|---|---|
| 5 | 13,77 | 3,44 | 19,43 | 1,09 | 18,34 |
| 11 | 32,02 | 3,18 | 17,45 | 1,41 | 16,04 |
| 17 | 46,29 | 3,44 | 15,26 | 1,30 | 13,96 |
| 23 | 57,64 | 3,11 | 13,16 | 1,07 | 12,09 |

**Otras cifras:**
- **LT:** C mejor que A, A′ y B en 24/24 combinaciones y en 6/6 réplicas ($p = 0{,}031$).
- **PC:** C mejor que A y B en 24/24 combinaciones y mejor que A′ en 21/24.
- **Pendientes:** la de A es de 2,43 mm/cm y la de B−C de −0,35 mm/cm.
- **PC por posición:** A pasa de 3,02 a 14,24 mm; A′ va de 0,75 a 1,34 mm, B de 2,77 a 4,54 mm y C de 0,48 a 0,62 mm.

**Tabla 3.1** (lecturas de calibre en mm; la referencia es la media):

| Réplica | LT1 | LT2 | LT3 | PC1 | PC2 | PC3 |
|---|---|---|---|---|---|---|
| R1 | 160 | 157 | 159 | 45 | 45 | 45 |
| R2 | 131 | 136 | 136 | 28 | 27 | 27 |
| R3 | 91 | 92 | 92 | 41 | 40 | 40 |
| R4 | 141 | 146 | 141 | 43 | 42 | 43 |
| R5 | 137 | 138 | 137 | 25 | 26 | 26 |
| R6 | 210 | 209 | 210 | 35 | 36 | 35 |

**Calibraciones:**
- B: RMS de 0,435 px y $f_x$ = 4502,3.
- C-air: RMS de 0,375 px y $f_x$ = 3313,7.
- Ambas: 4096 × 3072 px y damero de 4 × 4 esquinas interiores con cuadros de 20 mm.
- Ambos perfiles registran `opencv: 5.0.0` y `fish_morphometry: 0.1.0`.

**Repositorio citado en la tesis:** `https://github.com/Zequi20/FishmeterTPF`, etiqueta prevista `v1.0-tesis` y commit `0d71b69a8a7757b118d5f421f1958a0ecbb09214`.

## Paso 0: insumos y consistencia

Hacé este paso antes de cualquier otro pendiente.

1. **Inventario de insumos.** Listá dónde están realmente los siguientes archivos, con su ruta y cantidad de archivos, o indicá que no se encontraron:
   - las 72 imágenes;
   - los JSON de puntos;
   - `calibration_B.yaml`, `calibration_C_air.yaml`, `rail_reference_B.yaml` y la configuración del puerto plano;
   - `replicas.csv`;
   - el CSV maestro.
2. **Reproducción de la Tabla 4.2 y la Tabla 4.3.** Recalculalas desde el CSV maestro con la agregación descrita y compará cada celda con la tesis. Informá cualquier diferencia mayor de 0,01.
3. **Referencias de calibre.** Compará `lt_reference_mm` y `pc_reference_mm` del CSV con las medias de la Tabla 3.1. Las medias son: LT 158,67 / 134,33 / 91,67 / 142,67 / 137,33 / 209,67 y PC 45,00 / 27,33 / 40,33 / 42,67 / 25,67 / 35,33.
4. **Recuentos.** Comprobá 24/24, 21/24, 6/6 y las pendientes de 2,43 y −0,35 mm/cm.

Si el paso 0 encuentra discrepancias, ponelas al principio del informe con la etiqueta **DISCREPANCIA** y seguí con el resto.

## Pendientes que tenés que resolver

Cada sección indica dónde está el pendiente en la tesis, con el formato `archivo.tex:línea` relativo a la carpeta de la tesis.

### F1. Correspondencia entre la posición nominal y el riel

`capitulos/3-metodologia.tex:105-113`, Tabla 3.4.

La tabla dice que las posiciones nominales de 5, 11, 17 y 23 cm corresponden a lecturas del riel de 0, 60, 120 y 180 mm, con $z_{ref} = 0$ para B en la posición de 5 cm. Falta el desplazamiento entre el apoyo del carrito y el plano de simetría de cada réplica.

Determiná desde el código, los YAML y el CSV:

- **(a)** Qué significa `position_mm` (50, 110, 170, 230): ¿la distancia al vidrio o la lectura del riel? Y cómo se convierte en la profundidad que usa cada método.
- **(b)** Cómo calculan B y C la profundidad del plano de medición de cada imagen: fórmula, archivo y línea.
- **(c)** Si existe un desplazamiento entre el apoyo del carrito y el plano de simetría. Si existe, indicá su valor por réplica y de dónde sale.
- **(d)** Si la Tabla 3.4 es correcta tal como está.

Proponé la tabla corregida. Si el desplazamiento es por réplica y no por posición, proponé otra estructura de tabla.

### F2. Lado físico de los ArUco

`capitulos/3-metodologia.tex:115`.

Informá el lado $L_m$ (en mm) que usa el código para los marcadores id 0 (A, en el vidrio) e id 1 (A′, coplanar), y dónde está configurado. Si hay un valor medido con calibre registrado en algún archivo, informalo también.

La medición física con calibre la hace el usuario. Si el repo no la contiene, marcá el pendiente como **Parcial**.

### F3. Umbrales del riel

`capitulos/3-metodologia.tex:154`, Tabla 3.6 y Anexo D.

Verificá en el código que genera `rail_reference_B.yaml` si 1,0 px y 1,0° son:

- tolerancias configuradas (umbrales de aceptación), o
- errores o dispersiones observados.

Hacé lo mismo con el «error relativo de escala de 0,813 %» y con el residuo de $1{,}62 \times 10^{-13}$ mm. Indicá archivo y línea, y proponé la frase corregida.

### F4. Versiones del software

`capitulos/3-metodologia.tex:177`.

Informá las versiones de Python, OpenCV, NumPy, PyYAML y `fish_morphometry` que se usaron. Usá dos fuentes:

1. lo declarado en `pyproject.toml` u otros archivos de dependencias;
2. lo instalado en el entorno del proyecto (`python -c "import cv2, numpy, yaml; ..."` o `pip show`).

Confirmá en particular si OpenCV es realmente 5.0.0. Proponé el contenido de un `requirements.txt` congelado, sin agregarlo al repo.

### F5. Estado del repositorio y publicación

`capitulos/3-metodologia.tex:177`, `capitulos/3-metodologia.tex` en el párrafo de la tabla maestra (~línea 300) y `anexos/anexos.tex:120-138`.

- **(a)** Hash de HEAD, si existe la etiqueta `v1.0-tesis`, si el remoto es `Zequi20/FishmeterTPF` y si `0d71b69` es el commit con el que se generaron los resultados (comparalo con los metadatos de los JSON o del CSV, si los hay).
- **(b)** Compará el árbol real del repo con el que muestra el Anexo E:
  - `src/fish_morphometry/`, `tests/`, `calibrations/{air,water_pinhole,flatport}/`;
  - `data/raw/`, `data/annotations/`, `data/references/replicas.csv`;
  - `results/master.csv`, `results/L_z.csv`;
  - `analysis/make_figures.py`, `docs/`, `README.md`.

  Indicá qué existe, qué falta y qué está en `.gitignore`.
- **(c)** Escribí la lista exacta de pasos para publicar: qué archivos copiar a qué ruta, qué reglas de `.gitignore` cambiar, cómo mover las notas internas a `docs/dev/`, el `requirements.txt` y la creación y el push de la etiqueta. **No ejecutes ninguno de esos pasos.**
- **(d)** Señalá qué frases de la tesis hoy son falsas por este motivo. Por ejemplo, «Los archivos de datos … forman parte del repositorio».

### F6. MAE sobre capturas individuales

`capitulos/3-metodologia.tex:318`.

Por método, calculá el sesgo, el MAE y el MAPE de LT y de PC sobre las capturas individuales, sin promediar repeticiones (n = 70 para A y A′, n = 72 para B y C). Presentalo como una columna o una tabla adicional a la Tabla 4.2.

### F7. Recalcular con la intersección de 70 imágenes

`capitulos/4-resultados.tex:29`.

Recalculá la Tabla 4.2 y la Tabla 4.3 usando solo las 70 imágenes que tienen valor en los cuatro métodos. Informá las celdas que cambian y cuánto, y proponé la línea de texto que cierra el pendiente. Por ejemplo: «Con las 70 imágenes comunes, el MAE de LT de C pasa de 1,22 a X mm; el orden de los métodos no cambia».

### F8. Sensibilidad de C a $d$ y $μ_w$

`capitulos/4-resultados.tex:60-73`, Tabla 4.4.

Usá `sensitivity_c()` si sirve para esto. Si no, llamá a `measure_c` con una copia modificada de la configuración del puerto. Las variantes son:

- $d$ = 184 mm y $d$ = 276 mm (±20 %);
- $μ_w$ = 1,323 y $μ_w$ = 1,343.

La base es $d$ = 230 y $μ_w$ = 1,333. La tesis pide «una imagen de cada réplica». Si el costo lo permite, usá las 72 imágenes e informá también el resultado por réplica.

Para cada variante, informá:
- el cambio medio de LT en mm, con signo y absoluto;
- el mismo cambio en % de LT.

Completá con esos valores las cuatro filas de la tabla. Redactá también la oración de cierre: «Un error de ±20 % en $d$ cambia LT en menos de X mm (Y %) …». Ajustá la conclusión a lo que den los números, aunque contradiga la frase sugerida.

### F9. Prueba de signos para PC

`capitulos/4-resultados.tex:116`.

Con la réplica como unidad, para cada réplica promediá el error absoluto de PC sobre las 4 posiciones. Después calculá:

- **(a)** En cuántas de las 6 réplicas C tiene menor error que A′ y el valor de $p$ exacto de dos colas. Excluí los empates e informalos.
- **(b)** Lo mismo para C frente a A y C frente a B.

Proponé el texto: «Para PC, C fue mejor que \Aprime{} en $k$ de 6 réplicas ($p = \ldots$)».

### F10. Figura de errores con signo por combinación

`capitulos/4-resultados.tex:152`.

La figura muestra el error con signo de LT de cada una de las 24 combinaciones réplica–profundidad, por método. Son puntos individuales, no promedios, con el eje x en las posiciones y un desplazamiento horizontal por método. Agregá un panel equivalente para PC si se lee con claridad. Guardala como `figuras/fig4_4_errores_combinaciones.pdf` y proponé el `\caption`.

### F11. Corrida de $L(z)$, ancho numérico y cobertura

`capitulos/4-resultados.tex:211`, `:228` y `:237`.

1. Determiná cómo parametriza `measure_c` el plano de medición. Convertí la grilla $z$ = 0, 10, 20, …, 300 mm (distancia desde la cara interna del vidrio) a ese parámetro y documentá la conversión.
2. Ejecutá C sobre las 72 imágenes en toda la grilla y guardá `datos/L_z.csv` con las columnas `image_id`, `replicate_id`, `position_mm`, `repetition`, `z_mm`, `lt_mm` y `pc_mm`.
3. Verificá numéricamente que $L(z)$ sea monótona en cada imagen. Informá las excepciones.
4. Para tres escenarios, calculá el ancho relativo de $I_L$ (en % de la LT de calibre), promediado por posición nominal. En los escenarios acotados, evaluá $L$ en los extremos exactos de la ventana, no solo en la grilla. $z_0$ es la profundidad real del plano de medición de esa captura, según F1. Los escenarios son:
   - toda la pecera, [0, 300];
   - ±3 cm, $[z_0-30, z_0+30] ∩ [0, 300]$;
   - ±1 cm, $[z_0-10, z_0+10] ∩ [0, 300]$.

   Compará con la tabla analítica actual de la tesis (Tabla 4.5):

   | Escenario | 5 cm | 11 cm | 17 cm | 23 cm |
   |---|---|---|---|---|
   | Toda la pecera | 83 | 71 | 63 | 56 |
   | ±3 cm | 17 | 14 | 13 | 11 |
   | ±1 cm | 6 | 5 | 4 | 4 |

5. Calculá la **cobertura empírica** por escenario: la fracción de las 72 capturas cuya LT de calibre cae dentro de $I_L$.
6. **H3.** El criterio de la tesis es: «Cobertura ≥ 0,95 y ancho predicho dentro de la mitad del observado». Informá la cobertura y la razón entre el ancho analítico y el numérico, e indicá si se cumple cada parte del criterio. Proponé el veredicto («Se sostiene», «Se sostiene parcialmente» o «No se sostiene») y el párrafo correspondiente.
7. Hacé la figura `figuras/fig4_7_L_z_ejemplos.pdf` con $L(z)$ para dos imágenes de ejemplo de réplicas y posiciones distintas. Debe mostrar la LT de calibre como línea horizontal, la $z$ real como línea vertical y las ventanas de ±1 y ±3 cm sombreadas.

### F12. Bland–Altman de C frente al calibre

`capitulos/3-metodologia.tex:322` y `capitulos/4-resultados.tex:250`.

Para LT y para PC, calculá el sesgo y los límites de acuerdo (sesgo ± 1,96 DE) de C frente al calibre. Hacelo:

- sobre las 24 combinaciones promediadas, que es el análisis principal;
- sobre las 72 capturas, como dato complementario. En este caso indicá que las capturas no son independientes.

Hacé la figura `figuras/fig4_5_bland_altman_c.pdf`: diferencia frente al promedio, con líneas de sesgo y límites, y un panel para LT y otro para PC. Proponé el texto y el `\caption`.

### F13. Figura con una captura real

`capitulos/4-resultados.tex:250`.

Usá la imagen original de R3 a 23 cm, REP1, o otra repetición si a esa le falta algún dato. Dibujá los cuatro puntos marcados (desde `p1_x_px`…`p4_y_px` del CSV o desde el JSON de puntos) y el eje longitudinal. Recortá alrededor de la réplica si conviene. Guardala como `figuras/fig4_6_captura_R3_230.png` (y como PDF si la incrustación lo permite).

Informá para el `\caption` las cuatro estimaciones de LT y PC (A, A′, B y C) y la referencia de calibre de esa imagen.

### F14. Tabla maestra para el anexo

`anexos/anexos.tex:143`.

1. Calculá el SHA-256 del CSV maestro y el de la versión `.xlsx`.
2. Informá la cantidad de filas y la lista de columnas.
3. Generá `datos/tabla_maestra.tex`: un `longtable` en `\scriptsize` con las columnas imagen, método, LT estimada, LT de referencia, error de LT, PC estimada, PC de referencia, error de PC y estado. Usá coma decimal con 2 decimales.

### F15. Origen de las réplicas

`anexos/anexos.tex:148` y la columna «Origen / escala de impresión» de la Tabla 3.1.

Buscá en el repo, en `docs/` y en el CSV maestro cualquier dato sobre el modelo STL de cada réplica (origen o autor, escala de impresión, material) y fotografías individuales. Si no hay nada, marcalo **No resoluble desde el repositorio**.

## Pendientes manuales: no los resuelvas

Mencionalos en el informe solo con lo que se pide aquí.

- **Repetibilidad del marcado** (`capitulos/4-resultados.tex:157-170`, Tabla 4.6, y `capitulos/5-conclusiones.tex:53`). Requiere que el operador vuelva a marcar 12 imágenes sin ver el marcado anterior. Tu parte es:
  - **(a)** listar las 12 imágenes: una por réplica a 5 cm y a 23 cm, por defecto REP1;
  - **(b)** dejar en `scripts/` un script que, a partir de las anotaciones nuevas, calcule para cada punto p1–p4 la diferencia media y máxima en px y su efecto en mm sobre LT y PC con C;
  - **(c)** explicar dónde tiene que guardar el usuario las anotaciones nuevas para que el script las lea.
- **Lado físico de los ArUco medido con calibre:** solo informá lo que pide F2.
- **Comprobación con barra patrón sumergida:** fuera de alcance.

## Formato de `RESPUESTAS_PENDIENTES.md`

```
# Respuestas a los pendientes de la tesis (Fishmeter, <fecha>, commit <hash>)

## Paso 0 — Insumos y consistencia
<inventario de rutas; tabla de comparación de la Tabla 4.2 y la Tabla 4.3; referencias de calibre; DISCREPANCIAS al principio, si las hay>

## F1 — <título>
**Ubicación en la tesis:** capitulos/3-metodologia.tex:105-113
**Estado:** Resuelto | Parcial | No resoluble desde el repositorio
**Respuesta:** <1-3 oraciones>
**Valores:** <tabla Markdown>
**Fuente:** <archivo:línea | comando | scripts/xxx.py>
**Texto LaTeX propuesto:**
    <bloque listo para pegar: oración, filas de tabla o \caption>
**Advertencias:** <supuestos, limitaciones o contradicciones con lo que dice la tesis>

... (F2 a F15 y los pendientes manuales)

## Resumen
| ID | Pendiente | Estado | Archivos generados |
```

Antes de terminar, volvé a ejecutar cada script de `scripts/` desde cero y comprobá que reproduce las cifras del informe.
