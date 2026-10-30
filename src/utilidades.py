"""
Utilidades compartidas por los notebooks del proyecto.

Contiene:
    1. Rutas del proyecto.
    2. Catálogos (meses, delitos y sus nombres cortos, familias de delito).
    3. Estilo gráfico uniforme y función para guardar figuras.
    4. Funciones de texto y estadística descriptiva usadas en el EDA.

Mantener aquí lo que se repite evita inconsistencias entre notebooks.
"""

from __future__ import annotations

import unicodedata
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# ---------------------------------------------------------------------------
# 1. Rutas
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parents[1]

RUTA_RAW = RAIZ / "data" / "raw"
RUTA_PROCESSED = RAIZ / "data" / "processed"
RUTA_FIGURAS = RAIZ / "outputs" / "figures"

ARCHIVO_DENUNCIAS = RUTA_RAW / "denuncias_2022_2025.csv"
ARCHIVO_POBLACION = RUTA_RAW / "Estimaciones-y-Proyecciones-Municipales-2015-2035.xlsx"

ANIOS_ESTUDIO = [2022, 2023, 2024, 2025]

# ---------------------------------------------------------------------------
# 2. Catálogos
# ---------------------------------------------------------------------------

MESES_ORDEN = ["ene", "feb", "mar", "abr", "may", "jun",
               "jul", "ago", "sep", "oct", "nov", "dic"]
NUMERO_MES = {mes: i for i, mes in enumerate(MESES_ORDEN, start=1)}

# Los 12 delitos del estudio (nombre original del MP -> código de columna).
DELITOS = {
    "Homicidio": "homicidio",
    "Asesinato": "asesinato",
    "Robo": "robo",
    "Robo agravado": "robo_agravado",
    "Hurto": "hurto",
    "Hurto agravado": "hurto_agravado",
    "Extorsión": "extorsion",
    "Violación": "violacion",
    "Violación agravada": "violacion_agravada",
    "Violación con circunstancias especiales de agravación": "violacion_circ_especiales",
    "Agresión sexual": "agresion_sexual",
    "Agresión sexual con agravación de la pena": "agresion_sexual_agravada",
}

# Nombres cortos para que las etiquetas de las gráficas sean legibles.
NOMBRE_CORTO = {
    "Homicidio": "Homicidio",
    "Asesinato": "Asesinato",
    "Robo": "Robo",
    "Robo agravado": "Robo agravado",
    "Hurto": "Hurto",
    "Hurto agravado": "Hurto agravado",
    "Extorsión": "Extorsión",
    "Violación": "Violación",
    "Violación agravada": "Violación agravada",
    "Violación con circunstancias especiales de agravación": "Violación c. esp. agrav.",
    "Agresión sexual": "Agresión sexual",
    "Agresión sexual con agravación de la pena": "Agresión sexual agrav.",
}

# Agrupación temática (solo para ordenar y colorear gráficas; no se usa en el modelo).
FAMILIA_DELITO = {
    "Homicidio": "Contra la vida",
    "Asesinato": "Contra la vida",
    "Robo": "Contra el patrimonio",
    "Robo agravado": "Contra el patrimonio",
    "Hurto": "Contra el patrimonio",
    "Hurto agravado": "Contra el patrimonio",
    "Extorsión": "Extorsión",
    "Violación": "Sexuales",
    "Violación agravada": "Sexuales",
    "Violación con circunstancias especiales de agravación": "Sexuales",
    "Agresión sexual": "Sexuales",
    "Agresión sexual con agravación de la pena": "Sexuales",
}
ORDEN_DELITOS = list(DELITOS.keys())
CODIGOS_DELITO = list(DELITOS.values())
CODIGO_A_CORTO = {DELITOS[d]: NOMBRE_CORTO[d] for d in DELITOS}

# ---------------------------------------------------------------------------
# 3. Estilo gráfico
# ---------------------------------------------------------------------------
# Paleta categórica validada para daltonismo (orden fijo, no se recicla).

COLOR = {
    "azul": "#2a78d6",
    "naranja": "#eb6834",
    "aqua": "#1baf7a",
    "amarillo": "#eda100",
    "magenta": "#e87ba4",
    "verde": "#008300",
    "violeta": "#4a3aa7",
    "rojo": "#e34948",
    "gris": "#8a8984",
    "gris_claro": "#d9d8d4",
    "texto": "#0b0b0b",
    "texto_sec": "#52514e",
    "fondo": "#ffffff",
}
PALETA_CATEGORICA = [COLOR[c] for c in
                     ["azul", "naranja", "aqua", "amarillo",
                      "magenta", "verde", "violeta", "rojo"]]

COLOR_FAMILIA = {
    "Contra la vida": COLOR["azul"],
    "Contra el patrimonio": COLOR["naranja"],
    "Extorsión": COLOR["aqua"],
    "Sexuales": COLOR["violeta"],
}

# Secuencial (un solo tono, claro -> oscuro) para magnitudes.
CMAP_SECUENCIAL = LinearSegmentedColormap.from_list(
    "azules",
    ["#f4f8fd", "#cde2fb", "#9ec5f4", "#6da7ec",
     "#3987e5", "#256abf", "#184f95", "#0d366b"],
)
# Divergente (azul <-> rojo con gris neutro al centro) para correlaciones.
CMAP_DIVERGENTE = LinearSegmentedColormap.from_list(
    "azul_rojo",
    ["#104281", "#3987e5", "#9ec5f4", "#f0efec",
     "#f3b1ae", "#e34948", "#9e1f1f"],
)


def configurar_estilo() -> None:
    """Aplica un estilo sobrio y uniforme a todas las gráficas."""
    mpl.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 300,
        "figure.facecolor": COLOR["fondo"],
        "axes.facecolor": COLOR["fondo"],
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlepad": 22,
        "axes.labelsize": 10,
        "axes.labelcolor": COLOR["texto_sec"],
        "axes.edgecolor": COLOR["gris"],
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.prop_cycle": mpl.cycler(color=PALETA_CATEGORICA),
        "grid.color": "#ecebe8",
        "grid.linewidth": 0.8,
        "xtick.color": COLOR["texto_sec"],
        "ytick.color": COLOR["texto_sec"],
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "lines.linewidth": 2,
        "lines.markersize": 6,
        "patch.linewidth": 0,
    })


# Las explicaciones de cada figura van en su leyenda (pie de figura) del
# informe, no dentro de la imagen. Cambiar a True para volver a dibujarlas.
MOSTRAR_SUBTITULOS = False


def subtitulo(ax, texto: str) -> None:
    """Agrega un subtítulo gris debajo del título del eje (desactivado por defecto)."""
    if not MOSTRAR_SUBTITULOS:
        return
    ax.text(0, 1.02, texto, transform=ax.transAxes, fontsize=9,
            color=COLOR["texto_sec"], va="bottom", ha="left")


# Las figuras del informe llevan su fuente en el pie de figura del documento,
# no dentro de la imagen. Cambiar a True para volver a dibujarla en la figura.
MOSTRAR_FUENTE_EN_FIGURAS = False


def fuente(fig, texto: str = "Fuente: elaboración propia con datos del MP e INE.") -> None:
    """Nota de fuente en la esquina inferior izquierda de la figura (desactivada por defecto)."""
    if not MOSTRAR_FUENTE_EN_FIGURAS:
        return
    fig.text(0.01, 0.005, texto, fontsize=7.5, color=COLOR["gris"],
             ha="left", va="bottom")


# Figuras compuestas por varios gráficos: cada panel se identifica con un
# inciso (a), (b), ... al inicio de su título, en orden de lectura.
FIGURAS_CON_INCISOS = {
    "03_indice_por_delito", "02_distribucion_poblacion", "06_embudo_tasas",
    "13_pca_cargas_y_municipios", "02_observada_vs_suavizada", "01_metricas_por_k",
    "02_criterios_propios", "03_siluetas", "04_centroides_k3_vs_k5",
    "07_algoritmos_k3_k5", "05_evolucion_conglomerados", "08_mapas_por_conglomerado",
}


def etiquetar_paneles(fig) -> None:
    """Antepone (a), (b), ... al título de cada panel, de izquierda a derecha y de arriba abajo."""
    paneles = []
    for ax in fig.axes:
        titulos = [t for t in (ax.title, ax._left_title, ax._right_title) if t.get_text()]
        if titulos:
            pos = ax.get_position()
            paneles.append((round(-pos.y1, 2), pos.x0, titulos[0]))
    for i, (_, _, titulo) in enumerate(sorted(paneles, key=lambda p: (p[0], p[1]))):
        texto = titulo.get_text()
        if not texto.startswith("("):
            titulo.set_text(f"({chr(97 + i)}) {texto}")


def _quitar_textos_explicativos(fig) -> None:
    """Elimina los subtítulos grises de la figura (las explicaciones van en la leyenda)."""
    from matplotlib.colors import same_color
    for texto in list(fig.texts):
        if same_color(texto.get_color(), COLOR["texto_sec"]):
            texto.remove()


def guardar_figura(fig, nombre: str, carpeta: str) -> Path:
    """Guarda la figura en outputs/figures/<carpeta>/<nombre>.png (300 dpi)."""
    if not MOSTRAR_SUBTITULOS:
        _quitar_textos_explicativos(fig)
    if nombre in FIGURAS_CON_INCISOS:
        etiquetar_paneles(fig)
    destino = RUTA_FIGURAS / carpeta
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / f"{nombre}.png"
    fig.savefig(ruta, bbox_inches="tight", facecolor=COLOR["fondo"])
    return ruta


def formato_miles(ax, eje: str = "x") -> None:
    """Separador de miles en un eje (1,000 en lugar de 1000)."""
    fmt = mpl.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
    (ax.xaxis if eje == "x" else ax.yaxis).set_major_formatter(fmt)


# ---------------------------------------------------------------------------
# 4. Texto y estadística
# ---------------------------------------------------------------------------

def normalizar_texto(texto: str) -> str:
    """Minúsculas, sin tildes y sin espacios extremos (para cruzar nombres)."""
    sin_tildes = unicodedata.normalize("NFKD", str(texto))
    sin_tildes = sin_tildes.encode("ascii", "ignore").decode("ascii")
    return " ".join(sin_tildes.lower().split())


def coeficiente_gini(valores) -> float:
    """Índice de Gini (0 = reparto igual, 1 = concentración total)."""
    x = np.sort(np.asarray(valores, dtype=float))
    n = x.size
    if n == 0 or x.sum() == 0:
        return np.nan
    indices = np.arange(1, n + 1)
    return float((2 * np.sum(indices * x)) / (n * x.sum()) - (n + 1) / n)


def curva_lorenz(valores):
    """Devuelve (proporción acumulada de unidades, proporción acumulada del total)."""
    x = np.sort(np.asarray(valores, dtype=float))
    acumulado = np.concatenate([[0], np.cumsum(x)]) / x.sum()
    unidades = np.linspace(0, 1, x.size + 1)
    return unidades, acumulado


def resumen_distribucion(df: pd.DataFrame) -> pd.DataFrame:
    """Estadísticos descriptivos extendidos por columna numérica."""
    from scipy import stats

    filas = {}
    for col in df.columns:
        x = df[col].astype(float).dropna()
        q1, q3 = x.quantile([0.25, 0.75])
        filas[col] = {
            "media": x.mean(),
            "mediana": x.median(),
            "desv_est": x.std(),
            "CV": x.std() / x.mean() if x.mean() else np.nan,
            "min": x.min(),
            "Q1": q1,
            "Q3": q3,
            "max": x.max(),
            "asimetria": stats.skew(x),
            "curtosis": stats.kurtosis(x),
            "pct_ceros": (x == 0).mean() * 100,
        }
    return pd.DataFrame(filas).T


def estadistico_hopkins(X, proporcion: float = 0.1, repeticiones: int = 30,
                        semilla: int = 42) -> tuple[float, float]:
    """
    Estadístico de Hopkins para evaluar la tendencia de agrupamiento.

    H ≈ 0.5 -> datos distribuidos al azar (sin estructura de grupos).
    H -> 1  -> fuerte tendencia a formar grupos.

    Se repite varias veces con muestras distintas y se reporta media y
    desviación estándar para que el resultado sea estable y reproducible.
    """
    from sklearn.neighbors import NearestNeighbors

    X = np.asarray(X, dtype=float)
    n, d = X.shape
    m = max(1, int(proporcion * n))
    rng = np.random.default_rng(semilla)
    vecinos = NearestNeighbors(n_neighbors=2).fit(X)
    minimos, maximos = X.min(axis=0), X.max(axis=0)

    resultados = []
    for _ in range(repeticiones):
        # u: distancias desde puntos aleatorios uniformes al dato más cercano.
        aleatorios = rng.uniform(minimos, maximos, size=(m, d))
        u = vecinos.kneighbors(aleatorios, n_neighbors=1)[0][:, 0]
        # w: distancias desde datos reales a su vecino real más cercano.
        idx = rng.choice(n, size=m, replace=False)
        w = vecinos.kneighbors(X[idx], n_neighbors=2)[0][:, 1]
        resultados.append(u.sum() / (u.sum() + w.sum()))
    return float(np.mean(resultados)), float(np.std(resultados))


# ---------------------------------------------------------------------------
# 5. Conglomerados finales (K-means, k = 5)
# ---------------------------------------------------------------------------
# G1, G2, G4 y G5 están ordenados por intensidad -> rampa azul claro-oscuro.
# G3 tiene un perfil distinto (violencia contra las personas) -> tono contrastante.
# Validado para separación en mapas (todas las parejas, ΔE ≥ 18.6, incl. daltonismo).
COLOR_CLUSTER = {1: "#cde2fb", 2: "#6da7ec", 3: "#eb6834", 4: "#256abf", 5: "#0d366b"}
