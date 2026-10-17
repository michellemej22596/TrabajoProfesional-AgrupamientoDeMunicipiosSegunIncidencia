"""
Modelos y utilidades de evaluación para el agrupamiento.

Contiene:
    1. KMedoids: implementación del algoritmo PAM (Partitioning Around Medoids).
    2. Métricas internas de validación en un solo llamado.
    3. Estabilidad por remuestreo bootstrap (índice de Rand ajustado).
"""

from __future__ import annotations

import numpy as np
from scipy.spatial.distance import cdist
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.metrics import (adjusted_rand_score, calinski_harabasz_score,
                             davies_bouldin_score, silhouette_score)


# ---------------------------------------------------------------------------
# 1. K-medoids (PAM)
# ---------------------------------------------------------------------------

class KMedoids(BaseEstimator, ClusterMixin):
    """
    K-medoids con el algoritmo PAM (Kaufman y Rousseeuw, 1990).

    A diferencia de K-means, el centro de cada grupo (medoide) es una
    observación real (aquí, un municipio) y el algoritmo minimiza la suma de
    distancias —no de distancias al cuadrado—, por lo que es más robusto a
    valores atípicos.

    Fases:
        BUILD: elige k medoides iniciales de forma voraz (greedy).
        SWAP:  intercambia un medoide por un no medoide mientras el costo baje.

    Parámetros
    ----------
    n_clusters : número de grupos k.
    metric : métrica de distancia aceptada por scipy (p. ej. "euclidean", "cityblock").
    max_iter : máximo de iteraciones de la fase SWAP.
    """

    def __init__(self, n_clusters: int = 3, metric: str = "euclidean", max_iter: int = 300):
        self.n_clusters = n_clusters
        self.metric = metric
        self.max_iter = max_iter

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        D = cdist(X, X, metric=self.metric)
        n, k = D.shape[0], self.n_clusters

        # --- BUILD: el primer medoide minimiza la suma de distancias; los
        # siguientes son los que más reducen el costo total.
        medoides = [int(np.argmin(D.sum(axis=1)))]
        for _ in range(1, k):
            d_actual = D[:, medoides].min(axis=1)
            costo_si_agrego = np.minimum(D, d_actual[:, None]).sum(axis=0)
            costo_si_agrego[medoides] = np.inf
            medoides.append(int(np.argmin(costo_si_agrego)))
        medoides = np.array(medoides)

        # --- SWAP
        costo = D[:, medoides].min(axis=1).sum()
        for iteracion in range(self.max_iter):
            dm = D[:, medoides]
            orden = np.argsort(dm, axis=1)
            cercano = orden[:, 0]
            d1 = dm[np.arange(n), cercano]
            d2 = dm[np.arange(n), orden[:, 1]] if k > 1 else np.full(n, np.inf)

            mejor = (costo, None, None)
            for i in range(k):
                # Distancia de cada punto si se quita el medoide i
                base = np.where(cercano == i, d2, d1)
                costos = np.minimum(D, base[:, None]).sum(axis=0)
                costos[medoides] = np.inf
                h = int(np.argmin(costos))
                if costos[h] < mejor[0] - 1e-12:
                    mejor = (costos[h], i, h)
            if mejor[1] is None:
                break
            costo, i, h = mejor
            medoides[i] = h

        self.medoid_indices_ = medoides
        self.cluster_centers_ = X[medoides]
        self.labels_ = np.argmin(D[:, medoides], axis=1)
        self.inertia_ = float(costo)
        self.n_iter_ = iteracion + 1
        return self

    def predict(self, X):
        return np.argmin(cdist(np.asarray(X, float), self.cluster_centers_, metric=self.metric), axis=1)


# ---------------------------------------------------------------------------
# 2. Métricas internas
# ---------------------------------------------------------------------------

def metricas_internas(X, etiquetas) -> dict:
    """
    Silhouette (↑, de −1 a 1), Davies-Bouldin (↓, ≥ 0) y Calinski-Harabasz (↑).
    Las etiquetas −1 (ruido en DBSCAN/HDBSCAN) se excluyen del cálculo.
    """
    X = np.asarray(X, float)
    etiquetas = np.asarray(etiquetas)
    validos = etiquetas != -1
    grupos = np.unique(etiquetas[validos])
    salida = {"k": len(grupos), "pct_ruido": 100 * (1 - validos.mean())}
    if len(grupos) < 2:
        salida.update(silhouette=np.nan, davies_bouldin=np.nan, calinski_harabasz=np.nan,
                      pct_grupo_mayor=100.0, n_grupo_menor=int(validos.sum()))
        return salida
    Xv, ev = X[validos], etiquetas[validos]
    tamanos = np.bincount(np.searchsorted(grupos, ev))
    salida.update(
        silhouette=silhouette_score(Xv, ev),
        davies_bouldin=davies_bouldin_score(Xv, ev),
        calinski_harabasz=calinski_harabasz_score(Xv, ev),
        pct_grupo_mayor=100 * tamanos.max() / len(etiquetas),
        n_grupo_menor=int(tamanos.min()),
    )
    return salida


# ---------------------------------------------------------------------------
# 3. Estabilidad por bootstrap
# ---------------------------------------------------------------------------

def estabilidad_bootstrap(ajustar, X, n_boot: int = 50, semilla: int = 42) -> tuple[float, float]:
    """
    Estabilidad de un agrupamiento por remuestreo (enfoque de Hennig, 2007).

    `ajustar(X)` debe devolver etiquetas. Se ajusta el modelo con los datos
    completos (referencia) y con n_boot muestras bootstrap; en cada muestra se
    compara la partición con la de referencia, sobre los mismos municipios,
    mediante el índice de Rand ajustado (ARI: 1 = idéntica, 0 = azar).

    Devuelve (ARI medio, desviación estándar).
    """
    X = np.asarray(X, float)
    rng = np.random.default_rng(semilla)
    referencia = np.asarray(ajustar(X))
    valores = []
    for _ in range(n_boot):
        idx = np.unique(rng.choice(len(X), size=len(X), replace=True))
        etiquetas = np.asarray(ajustar(X[idx]))
        valores.append(adjusted_rand_score(referencia[idx], etiquetas))
    return float(np.mean(valores)), float(np.std(valores))


# ---------------------------------------------------------------------------
# 4. Utilidades de interpretación
# ---------------------------------------------------------------------------

def ordenar_grupos(X, etiquetas) -> np.ndarray:
    """
    Renumera los grupos de 1 a k según su intensidad media (promedio de las
    variables estandarizadas): 1 = menor incidencia, k = mayor.

    Así el "grupo 1" significa lo mismo en todos los algoritmos y los colores
    de las gráficas son comparables.
    """
    X = np.asarray(X, float)
    etiquetas = np.asarray(etiquetas)
    grupos = np.unique(etiquetas)
    intensidad = {g: X[etiquetas == g].mean() for g in grupos}
    orden = sorted(grupos, key=lambda g: intensidad[g])
    mapa = {g: i + 1 for i, g in enumerate(orden)}
    return np.array([mapa[e] for e in etiquetas])


def estadistico_gap(X, k_max: int = 10, n_ref: int = 20, semilla: int = 42):
    """
    Estadístico gap de Tibshirani, Walther y Hastie (2001) para K-means.

    Compara log(W_k) de los datos con el de datos de referencia uniformes
    (generados en la caja alineada con las componentes principales).
    Regla 1-SE: el k óptimo es el menor k tal que Gap(k) ≥ Gap(k+1) − s(k+1).
    Devuelve (gap, s, k_optimo) con índices k = 1..k_max.
    """
    from sklearn.cluster import KMeans

    X = np.asarray(X, float)
    rng = np.random.default_rng(semilla)
    centro = X - X.mean(axis=0)
    _, _, Vt = np.linalg.svd(centro, full_matrices=False)
    proy = centro @ Vt.T
    lo, hi = proy.min(axis=0), proy.max(axis=0)

    def log_w(Z, k):
        return np.log(KMeans(k, n_init=10, random_state=semilla).fit(Z).inertia_)

    gap, s = [], []
    for k in range(1, k_max + 1):
        ref = [log_w(rng.uniform(lo, hi, size=proy.shape) @ Vt, k) for _ in range(n_ref)]
        gap.append(np.mean(ref) - log_w(X, k))
        s.append(np.std(ref) * np.sqrt(1 + 1 / n_ref))
    gap, s = np.array(gap), np.array(s)
    k_opt = next((k for k in range(1, k_max) if gap[k - 1] >= gap[k] - s[k]), k_max)
    return gap, s, k_opt


def estabilidad_por_grupo(ajustar, X, n_boot: int = 100, semilla: int = 42) -> np.ndarray:
    """
    Estabilidad de cada grupo por separado (índice de Jaccard, Hennig 2007).

    Para cada remuestreo bootstrap se busca, para cada grupo original, el
    grupo del remuestreo que más se le parece (máximo Jaccard sobre los
    municipios presentes en ambos). Se devuelve el Jaccard medio de cada
    grupo, en el orden de `ordenar_grupos` (grupo 1 = menor intensidad).

    Interpretación (Hennig): ≥ 0.75 estable · 0.6–0.75 patrón real pero
    difuso · < 0.5 grupo que "se disuelve".
    """
    X = np.asarray(X, float)
    rng = np.random.default_rng(semilla)
    referencia = ordenar_grupos(X, ajustar(X))
    grupos = np.unique(referencia)
    jaccard = np.zeros((n_boot, len(grupos)))
    for b in range(n_boot):
        idx = np.unique(rng.choice(len(X), size=len(X), replace=True))
        etiquetas = np.asarray(ajustar(X[idx]))
        ref_b = referencia[idx]
        for i, g in enumerate(grupos):
            A = set(np.flatnonzero(ref_b == g))
            mejor = 0.0
            for h in np.unique(etiquetas):
                B = set(np.flatnonzero(etiquetas == h))
                mejor = max(mejor, len(A & B) / len(A | B))
            jaccard[b, i] = mejor
    return jaccard.mean(axis=0)
