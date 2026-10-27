#!/usr/bin/env python3
"""Reune las figuras, tablas y graficos activos de la tesis en ``adjuntos/``.

Las imagenes conservan el formato del recurso usado por LaTeX. Las figuras
dibujadas directamente con TikZ se exportan desde sus PNG ya renderizados. Las
tablas se guardan como fragmentos LaTeX editables, sin alterar los originales.
"""

from __future__ import annotations

import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "adjuntos"
IMAGE_OUTPUT = OUTPUT / "imagenes"
TABLE_OUTPUT = OUTPUT / "tablas"
GRAPH_OUTPUT = OUTPUT / "graficos"

TEX_FILES = [
    ROOT / "capitulos/1-introduccion.tex",
    ROOT / "capitulos/2-marco.tex",
    ROOT / "capitulos/3-metodologia.tex",
    ROOT / "capitulos/4-resultados.tex",
    ROOT / "capitulos/5-conclusiones.tex",
    ROOT / "anexos/anexos.tex",
    ROOT / "anexos/tabla_maestra.tex",
]


@dataclass(frozen=True)
class Metadata:
    number: str
    slug: str
    title: str


@dataclass(frozen=True)
class Block:
    label: str
    source: Path
    start: int
    end: int
    text: str


FIGURES = {
    "fig:1-1": Metadata("1", "configuracion_conceptual_camara_vidrio_agua", "Configuración conceptual de cámara, vidrio, agua y rayos refractados"),
    "fig:2-1": Metadata("2", "flujo_teorico_investigacion", "Flujo teórico simplificado de la investigación"),
    "fig:2-2": Metadata("3", "puntos_anatomicos_medidas_morfometricas", "Puntos anatómicos y medidas morfométricas consideradas"),
    "fig:2-3": Metadata("4", "modelo_refractivo_puerto_plano", "Modelo refractivo de puerto plano"),
    "fig:2-5": Metadata("5", "escala_aparente_marcador_profundidad", "Escala aparente de un marcador según su profundidad"),
    "fig:2-4": Metadata("6", "cuatro_rutas_conversion_metrica", "Las cuatro rutas de conversión métrica lado a lado"),
    "fig:3-1": Metadata("7", "replicas_peces_impresas_pla", "Réplicas de peces impresas en PLA utilizadas en el experimento"),
    "fig:3-esquema": Metadata("8", "esquema_montaje_experimental", "Esquema acotado del montaje experimental"),
    "fig:3-2": Metadata("9", "montaje_replica_marcador_aruco_coplanar", "Montaje de una réplica junto con el marcador ArUco coplanar"),
    "fig:3-3": Metadata("10", "damero_marcador_aruco_pecera", "Damero y marcador ArUco colocados dentro de la pecera"),
    "fig:3-4": Metadata("11", "interfaz_fishmeter_marcacion_metodos", "Interfaz de Fishmeter para la marcación y comparación de métodos"),
    "fig:3-5": Metadata("12", "puntos_anatomicos_longitud_profundidad", "Puntos anatómicos empleados para la longitud total y la profundidad corporal"),
    "fig:3-6": Metadata("13", "instrumentos_medicion_replica", "Instrumentos y disposición utilizados para medir físicamente una réplica"),
    "fig:3-flujo": Metadata("14", "flujo_procesamiento_imagen", "Flujo de procesamiento por imagen"),
    "fig:4-1": Metadata("15", "mae_metodo_longitud_profundidad", "MAE por método para longitud total y profundidad corporal"),
    "fig:4-2": Metadata("16", "mae_longitud_metodo_profundidad", "MAE de longitud total por método y profundidad"),
    "fig:4-errores": Metadata("17", "error_combinacion_replica_profundidad", "Error con signo por combinación réplica–profundidad"),
    "fig:4-3": Metadata("18", "ancho_intervalo_profundidad_desconocida", "Ancho relativo del intervalo por profundidad desconocida"),
    "fig:4-Lz": Metadata("19", "longitud_estimada_c_profundidad_supuesta", "Longitud estimada por C en función de la profundidad supuesta"),
    "fig:4-BA": Metadata("20", "bland_altman_c_calibre", "Bland-Altman de C frente al calibre"),
    "fig:4-captura": Metadata("21", "captura_puntos_anatomicos_marcados", "Captura real con los cuatro puntos anatómicos marcados"),
    "fig:5-1": Metadata("22", "diagrama_decision_conversion_metrica", "Diagrama de decisión para la conversión métrica monocular a través de un vidrio plano"),
    "fig:A-1": Metadata("A1", "vista_capturas_identificadores", "Vista conjunta de las capturas y sus identificadores"),
    "fig:B-1": Metadata("B1", "configuracion_puerto_plano", "Parámetros visibles de la configuración del puerto plano"),
    "fig:G-1": Metadata("G1", "replicas_identificadas", "Réplicas utilizadas en el experimento con su identificador"),
    "fig:H-1": Metadata("H1", "pecera_experimento", "Pecera utilizada en el experimento"),
    "fig:H-2": Metadata("H2", "instrumentos_medicion_manipulacion", "Instrumentos de medición y de manipulación"),
}


TABLES = {
    "tab:trazabilidad": Metadata("1", "trazabilidad_preguntas_objetivos_hipotesis", "Trazabilidad entre preguntas, objetivos, hipótesis, resultados y conclusiones"),
    "tab:antecedentes": Metadata("2", "matriz_comparativa_antecedentes", "Matriz comparativa de antecedentes relacionados con la medición morfométrica y la corrección refractiva"),
    "tab:replicas": Metadata("3", "replicas_referencias_fisicas_calibre", "Réplicas y referencias físicas medidas con calibre"),
    "tab:operacionalizacion": Metadata("4", "operacionalizacion_variables", "Operacionalización de las variables"),
    "tab:posiciones": Metadata("5", "posicion_replica_lectura_riel", "Correspondencia entre la posición nominal de la réplica y la lectura del riel"),
    "tab:puerto": Metadata("6", "parametros_puerto_plano_ruta_c", "Parámetros del puerto plano utilizados por la ruta C"),
    "tab:riel": Metadata("7", "referencia_geometrica_riel_ruta_b", "Referencia geométrica del riel utilizada por la ruta B"),
    "tab:recorridos": Metadata("8", "recorrido_metodos_fishmeter", "Recorrido de cada método en Fishmeter, desde los píxeles hasta la medición"),
    "tab:registros": Metadata("9", "registros_csv_tratamiento", "Registros del CSV y su tratamiento en el análisis"),
    "tab:calibraciones": Metadata("10", "calibraciones_camara_rutas_b_c", "Calibraciones de cámara utilizadas por las rutas B y C"),
    "tab:sensibilidad": Metadata("11", "sensibilidad_longitud_ruta_c", "Sensibilidad de la longitud total estimada por C a los parámetros medidos a mano"),
    "tab:agregados": Metadata("12", "errores_medios_por_metodo", "Errores medios por método después de resumir las repeticiones técnicas"),
    "tab:posiciones-mae": Metadata("13", "mae_longitud_por_posicion", "MAE de longitud total por posición de la réplica"),
    "tab:intervalo": Metadata("14", "ancho_intervalo_profundidad", "Ancho relativo del intervalo según la profundidad y el conocimiento disponible"),
    "tab:hipotesis": Metadata("15", "contraste_hipotesis", "Contraste de hipótesis"),
    "tab:regla": Metadata("16", "regla_decision_conversion", "Regla de decisión sobre la conversión que se debe utilizar"),
    "tab:cumplimiento": Metadata("17", "cumplimiento_objetivos_especificos", "Matriz de cumplimiento de los objetivos específicos"),
    "tab:maestra": Metadata("F1", "maestra_estimaciones_imagen_metodo", "Tabla maestra de referencias de calibre y estimaciones por imagen y método"),
    "tab:lecturas-calibre": Metadata("G1", "lecturas_calibre_replicas", "Lecturas de calibre de las réplicas"),
}


GRAPHS = {
    "fig:4-1": (Metadata("1", "mae_metodo_longitud_profundidad", "MAE por método para longitud total y profundidad corporal"), ROOT / "figuras/fig4_1_mae_por_metodo.pdf"),
    "fig:4-2": (Metadata("2", "mae_longitud_metodo_profundidad", "MAE de longitud total por método y profundidad"), ROOT / "figuras/fig4_2_mae_lt_profundidad.pdf"),
    "fig:4-errores": (Metadata("3", "error_combinacion_replica_profundidad", "Error con signo por combinación réplica–profundidad"), ROOT / "figuras/fig4_errores_combinaciones.pdf"),
    "fig:4-3": (Metadata("4", "ancho_intervalo_profundidad_desconocida", "Ancho relativo del intervalo por profundidad desconocida"), ROOT / "figuras/fig4_3_ancho_intervalo.pdf"),
    "fig:4-Lz": (Metadata("5", "longitud_estimada_profundidad_supuesta", "Longitud estimada por C en función de la profundidad supuesta"), ROOT / "figuras/fig4_L_z_ejemplos.pdf"),
    "fig:4-BA": (Metadata("6", "bland_altman_c_calibre", "Bland-Altman de C frente al calibre"), ROOT / "figuras/fig4_bland_altman_c.pdf"),
}


TIKZ_RENDERS = {
    "fig:2-5": ROOT / "figuras/tikz/tikz_1.png",
    "fig:2-4": ROOT / "figuras/tikz/tikz_2.png",
    "fig:3-esquema": ROOT / "figuras/tikz/tikz_3.png",
    "fig:3-flujo": ROOT / "figuras/tikz/tikz_4.png",
    "fig:5-1": ROOT / "figuras/tikz/tikz_5.png",
}


def active_line(line: str) -> bool:
    """Indica si una linea no esta anulada por un comentario LaTeX."""
    return not line.lstrip().startswith("%")


def extract_blocks(kind: str) -> dict[str, Block]:
    environments = ("figure",) if kind == "figure" else ("table", "longtable")
    begin_pattern = re.compile(r"\\begin\{(" + "|".join(environments) + r")\}(?:\[[^]]*\])?")
    label_pattern = re.compile(r"\\label\{((?:fig|tab):[^}]+)\}")
    blocks: dict[str, Block] = {}

    for source in TEX_FILES:
        lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
        index = 0
        while index < len(lines):
            line = lines[index]
            match = begin_pattern.search(line) if active_line(line) else None
            if not match:
                index += 1
                continue

            environment = match.group(1)
            end_pattern = re.compile(rf"\\end\{{{re.escape(environment)}\}}")
            end = index
            while end < len(lines):
                if active_line(lines[end]) and end_pattern.search(lines[end]):
                    break
                end += 1
            if end == len(lines):
                raise RuntimeError(f"Entorno {environment} sin cierre en {source}:{index + 1}")

            text = "".join(lines[index : end + 1])
            labels = label_pattern.findall("".join(line for line in lines[index : end + 1] if active_line(line)))
            if len(labels) != 1:
                raise RuntimeError(f"Se esperaba una etiqueta en {source}:{index + 1}; se encontraron {labels}")
            label = labels[0]
            blocks[label] = Block(label, source, index + 1, end + 1, text)
            index = end + 1

    return blocks


def resolve_graphic(reference: str) -> Path:
    reference_path = Path(reference)
    candidates = [ROOT / reference_path, ROOT / "figuras" / reference_path, ROOT / "figuras/originales" / reference_path]
    if not reference_path.suffix:
        candidates = [candidate.with_suffix(extension) for candidate in candidates for extension in (".pdf", ".png", ".jpg", ".jpeg")]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"No se encontro el recurso grafico {reference}")


def filename_prefix(kind: str, number: str) -> str:
    normalized = number.lower()
    if normalized.isdigit():
        normalized = f"{int(normalized):02d}"
    return f"{kind}_{normalized}"


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    IMAGE_OUTPUT.mkdir(parents=True, exist_ok=True)
    TABLE_OUTPUT.mkdir(parents=True, exist_ok=True)
    GRAPH_OUTPUT.mkdir(parents=True, exist_ok=True)

    figure_blocks = extract_blocks("figure")
    table_blocks = extract_blocks("table")

    if set(figure_blocks) != set(FIGURES):
        raise RuntimeError(f"Las figuras encontradas no coinciden con el inventario: {sorted(set(figure_blocks) ^ set(FIGURES))}")
    if set(table_blocks) != set(TABLES):
        raise RuntimeError(f"Las tablas encontradas no coinciden con el inventario: {sorted(set(table_blocks) ^ set(TABLES))}")

    manifest_rows: list[dict[str, str]] = []
    image_rows: list[tuple[Metadata, str, Block]] = []
    graph_rows: list[tuple[str, Metadata, str, Block]] = []
    table_rows: list[tuple[Metadata, str, Block]] = []

    include_pattern = re.compile(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}")
    for label, metadata in FIGURES.items():
        block = figure_blocks[label]
        include = include_pattern.search(block.text)
        graphic = resolve_graphic(include.group(1)) if include else TIKZ_RENDERS[label]
        destination_name = f"{filename_prefix('figura', metadata.number)}_{metadata.slug}{graphic.suffix.lower()}"
        destination = IMAGE_OUTPUT / destination_name
        shutil.copy2(graphic, destination)
        image_rows.append((metadata, destination_name, block))
        manifest_rows.append(
            {
                "tipo": "figura",
                "numero": metadata.number,
                "etiqueta_latex": label,
                "titulo": metadata.title,
                "archivo_adjunto": relative(destination),
                "archivo_imagen": "",
                "recurso_original": relative(graphic),
                "ubicacion_latex": f"{relative(block.source)}:{block.start}-{block.end}",
            }
        )

    for label, (metadata, graphic) in GRAPHS.items():
        block = figure_blocks[label]
        if not graphic.is_file():
            raise FileNotFoundError(f"No se encontro el grafico {graphic}")
        destination_name = f"{filename_prefix('grafico', metadata.number)}_{metadata.slug}{graphic.suffix.lower()}"
        destination = GRAPH_OUTPUT / destination_name
        shutil.copy2(graphic, destination)
        graph_rows.append((label, metadata, destination_name, block))
        manifest_rows.append(
            {
                "tipo": "grafico",
                "numero": metadata.number,
                "etiqueta_latex": label,
                "titulo": metadata.title,
                "archivo_adjunto": relative(destination),
                "archivo_imagen": "",
                "recurso_original": relative(graphic),
                "ubicacion_latex": f"{relative(block.source)}:{block.start}-{block.end}",
            }
        )

    for label, metadata in TABLES.items():
        block = table_blocks[label]
        destination_name = f"{filename_prefix('tabla', metadata.number)}_{metadata.slug}.tex"
        destination = TABLE_OUTPUT / destination_name
        header = (
            f"% Tabla {metadata.number}: {metadata.title}.\n"
            f"% Etiqueta original: {label}.\n"
            f"% Fuente: {relative(block.source)}, lineas {block.start}-{block.end}.\n"
            "% Fragmento extraido automaticamente; requiere el preambulo de main.tex.\n\n"
        )
        destination.write_text(header + block.text, encoding="utf-8")
        table_rows.append((metadata, destination_name, block))
        image_name = f"{filename_prefix('tabla', metadata.number)}_{metadata.slug}.png"
        image_path = OUTPUT / "tablas_imagen" / image_name
        manifest_rows.append(
            {
                "tipo": "tabla",
                "numero": metadata.number,
                "etiqueta_latex": label,
                "titulo": metadata.title,
                "archivo_adjunto": relative(destination),
                "archivo_imagen": relative(image_path) if image_path.is_file() else "",
                "recurso_original": relative(block.source),
                "ubicacion_latex": f"{relative(block.source)}:{block.start}-{block.end}",
            }
        )

    manifest_path = OUTPUT / "indice_adjuntos.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("tipo", "numero", "etiqueta_latex", "titulo", "archivo_adjunto", "archivo_imagen", "recurso_original", "ubicacion_latex"),
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    rendered_table_images = sum(1 for metadata in TABLES.values() if (OUTPUT / "tablas_imagen" / f"{filename_prefix('tabla', metadata.number)}_{metadata.slug}.png").is_file())
    readme_lines = [
        "# Adjuntos: figuras, tablas y gráficos\n\n",
        "Esta carpeta reúne las figuras, tablas y gráficos activos de la tesis con nombres descriptivos. "
        "Los archivos fuente del proyecto no se modifican: las figuras se copian en su formato original "
        "y las tablas se extraen como fragmentos LaTeX editables. Los gráficos se conservan como PDF vectoriales.\n\n",
        f"Inventario: **{len(image_rows)} figuras**, **{len(graph_rows)} gráficos**, **{len(table_rows)} tablas editables** y **{rendered_table_images} tablas en PNG**. "
        "El archivo `indice_adjuntos.csv` relaciona cada adjunto con su etiqueta, título y ubicación de origen.\n\n",
        "No se incluyen el logotipo, el membrete, las 72 capturas crudas de `datos/imagenes` ni los entornos comentados, "
        "porque no son figuras o tablas activas del documento. Las figuras dibujadas con TikZ se incluyen como PNG renderizados.\n\n",
        "## Imágenes\n\n",
        "| Número | Etiqueta | Título | Archivo |\n",
        "|---:|---|---|---|\n",
    ]
    for metadata, destination_name, block in image_rows:
        label = next(label for label, value in FIGURES.items() if value == metadata)
        readme_lines.append(f"| {metadata.number} | `{label}` | {metadata.title} | [`{destination_name}`](imagenes/{destination_name}) |\n")

    readme_lines.extend(
        [
            "\n## Gráficos\n\n",
            "| Número | Etiqueta | Título | Archivo vectorial |\n",
            "|---:|---|---|---|\n",
        ]
    )
    for label, metadata, destination_name, block in graph_rows:
        readme_lines.append(f"| {metadata.number} | `{label}` | {metadata.title} | [`{destination_name}`](graficos/{destination_name}) |\n")

    readme_lines.extend(
        [
            "\n## Tablas\n\n",
            "| Número | Etiqueta | Título | Archivo editable | Imagen |\n",
            "|---:|---|---|---|---|\n",
        ]
    )
    for metadata, destination_name, block in table_rows:
        label = next(label for label, value in TABLES.items() if value == metadata)
        image_name = f"{filename_prefix('tabla', metadata.number)}_{metadata.slug}.png"
        image_path = OUTPUT / "tablas_imagen" / image_name
        image_link = f"[`{image_name}`](tablas_imagen/{image_name})" if image_path.is_file() else "—"
        readme_lines.append(f"| {metadata.number} | `{label}` | {metadata.title} | [`{destination_name}`](tablas/{destination_name}) | {image_link} |\n")

    readme_lines.extend(
        [
            "\n## Regeneración\n\n",
            "Desde la raíz del proyecto:\n\n",
            "```bash\n",
            "python3 scripts/generar_adjuntos.py\n",
            "python3 scripts/renderizar_tablas.py\n",
            "```\n",
        ]
    )
    (OUTPUT / "README.md").write_text("".join(readme_lines), encoding="utf-8")

    print(f"Adjuntos generados: {len(image_rows)} figuras, {len(graph_rows)} graficos y {len(table_rows)} tablas en {relative(OUTPUT)}/")


if __name__ == "__main__":
    main()
