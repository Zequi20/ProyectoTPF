# Re-run de B con la coordenada de riel corregida

Generado: 2026-10-29T19:26:19+00:00 · script `analysis/re_run_b.py`

## Qué cambió

- Entrada de riel: `position_mm − 50 mm` (50/110/170/230 → 0/60/120/180 mm).
- Sin cambios: puntos p1–p4, eje, tolerancia, offset de réplica (0 mm asumido), perfil B y referencia cámara–rail (hashes verificados).
- Perfil B `eb245104cb46…`, referencia `1f0659fd92c5…`.
- Capturas recalculadas: 72; con estado ERROR: 0.

## Error frente al calibre (n = 24 réplica–posición)

| Método | Sesgo LT % | MAPE LT % | Sesgo PC % | MAPE PC % |
|---|---:|---:|---:|---:|
| A | -25,68 | 25,68 | -25,25 | 25,25 |
| A′ | +2,28 | 2,28 | +2,49 | 2,78 |
| B_original | +11,24 | 11,24 | +9,96 | 9,96 |
| B_re_run | +0,07 | 0,73 | -1,09 | 1,26 |
| C | +0,79 | 0,88 | +0,60 | 1,62 |

## Sesgo de LT por posición (%)

| Método | 50 mm | 110 mm | 170 mm | 230 mm | Pendiente (%/100 mm) |
|---|---:|---:|---:|---:|---:|
| A | -9,46 | -21,96 | -31,78 | -39,54 | -16,68 |
| A′ | +2,40 | +2,22 | +2,39 | +2,11 | -0,12 |
| B_original | +13,34 | +12,03 | +10,49 | +9,10 | -2,38 |
| B_re_run | -0,22 | +0,31 | +0,22 | -0,03 | +0,08 |
| C | +0,47 | +0,97 | +0,93 | +0,77 | +0,14 |

## Consistencia entre posiciones (sin calibre)

CV medio de la misma réplica medida en las cuatro posiciones.

| Método | CV LT % | CV PC % |
|---|---:|---:|
| A | 17,48 | 17,95 |
| A′ | 0,29 | 1,00 |
| B_original | 1,66 | 1,97 |
| B_re_run | 0,31 | 0,65 |
| C | 0,30 | 0,68 |

## Concordancia con C por captura

| Método | media (X − C) LT mm | media |X − C| LT mm | media |X − C| PC mm |
|---|---:|---:|---:|
| A | -38,84 | 38,84 | 9,45 |
| A′ | +2,24 | 2,34 | 0,71 |
| B_original | +15,26 | 15,26 | 3,38 |
| B_re_run | -1,02 | 1,02 | 0,61 |

Combinaciones réplica–posición donde el re-run reduce |error|: LT 24/24, PC 22/24.

## Advertencias

- Las lecturas de PC de R1 y R2 se anotaron con un cero de más (450 por 45 mm; 280/270 por 28/27 mm) y están corregidas en la tabla maestra.
- El desplazamiento de 10 mm del plano de simetría respecto del apoyo se compensó físicamente en el montaje; el procesamiento usa 0 mm.
- B sigue en `PENDING_VALIDATION`: una menor discrepancia con el calibre no reemplaza la validación física con regla sumergida en cada posición.
