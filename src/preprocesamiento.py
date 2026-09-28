"""
Funciones de preprocesamiento de las tasas delictivas.

Suavizado bayesiano empírico (Marshall, 1991)
---------------------------------------------
En municipios con poca población, unas pocas denuncias producen tasas muy
altas o muy bajas solo por azar. El suavizado bayesiano empírico "encoge"
cada tasa hacia la tasa global en proporción a lo poco confiable que es:

    tasa_suavizada_i = m + w_i · (r_i − m)

    r_i : tasa observada del municipio i          (O_i / n_i)
    m   : tasa global                             (Σ O / Σ n)
    A   : varianza "real" entre municipios        (s² − m / n̄, mínimo 0)
    w_i : peso de la tasa propia                  A / (A + m / n_i)

- Municipio grande (n_i alto)    -> w_i ≈ 1 -> casi no cambia.
- Municipio pequeño (n_i bajo)   -> w_i menor -> se acerca a la tasa global.
- Delito frecuente (A grande)    -> w_i ≈ 1 para casi todos.
- Delito poco frecuente          -> más encogimiento.

Referencia: Marshall, R. J. (1991). Mapping disease and mortality rates using
empirical Bayes estimators. Journal of the Royal Statistical Society, Series C,
40(2), 283–294.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def suavizado_bayes_empirico(conteos: pd.Series, exposicion: pd.Series,
                             por: float = 100_000) -> pd.DataFrame:
    """
    Suavizado bayesiano empírico global (estimador de momentos de Marshall).

    Parámetros
    ----------
    conteos : denuncias observadas por municipio (O_i).
    exposicion : población en riesgo por municipio (n_i), p. ej. persona-años.
    por : escala de la tasa (100,000 = tasa por 100 mil habitantes).

    Devuelve
    --------
    DataFrame con columnas: tasa_observada, tasa_suavizada, peso.
    Los atributos .attrs guardan la tasa global (m) y la varianza A.
    """
    O = conteos.astype(float)
    n = exposicion.astype(float).reindex(O.index)
    r = O / n
    m = O.sum() / n.sum()
    s2 = (n * (r - m) ** 2).sum() / n.sum()
    A = max(s2 - m / n.mean(), 0.0)
    w = A / (A + m / n) if A > 0 else pd.Series(0.0, index=O.index)
    suavizada = m + w * (r - m)

    salida = pd.DataFrame({
        "tasa_observada": r * por,
        "tasa_suavizada": suavizada * por,
        "peso": w,
    })
    salida.attrs.update({"tasa_global": m * por, "varianza_A": A * por ** 2})
    return salida
