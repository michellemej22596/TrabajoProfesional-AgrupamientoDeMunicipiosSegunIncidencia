import pandas as pd

# ---------------------------------------------------------
# 1. Cargar datos
# ---------------------------------------------------------

archivo_entrada = "denuncias_2022_2025.csv"

df = pd.read_csv(
    archivo_entrada,
    encoding="utf-8-sig"
)

# ---------------------------------------------------------
# 2. Ajustar tipos de datos
# ---------------------------------------------------------

df["Anio"] = pd.to_numeric(df["Anio"], errors="coerce").astype("Int64")
df["Denuncias"] = pd.to_numeric(df["Denuncias"], errors="coerce").fillna(0)

# ---------------------------------------------------------
# 3. Crear catálogo de municipios
# ---------------------------------------------------------
# Se utilizan Departamento + Municipio porque algunos nombres
# de municipios se repiten en departamentos diferentes.

municipios = (
    df[["Departamento", "Municipio"]]
    .drop_duplicates()
    .sort_values(["Departamento", "Municipio"])
    .reset_index(drop=True)
)

# Años considerados en la investigación
anios = pd.DataFrame({
    "Anio": [2022, 2023, 2024, 2025]
})

# ---------------------------------------------------------
# 4. Crear todas las combinaciones año-municipio
# ---------------------------------------------------------
# Esto garantiza que incluso si un municipio no tiene ningún
# registro en un año determinado, la fila aparecerá.

base = anios.merge(
    municipios,
    how="cross"
)

# ---------------------------------------------------------
# 5. Sumar denuncias por año, departamento, municipio y delito
# ---------------------------------------------------------
# Como Mes y Grado_Delito no forman parte del groupby,
# sus registros se suman automáticamente.

agrupado = (
    df.groupby(
        ["Anio", "Departamento", "Municipio", "Delito"],
        as_index=False
    )["Denuncias"]
    .sum()
)

# ---------------------------------------------------------
# 6. Pivotear delitos a columnas
# ---------------------------------------------------------

pivot = (
    agrupado.pivot_table(
        index=["Anio", "Departamento", "Municipio"],
        columns="Delito",
        values="Denuncias",
        aggfunc="sum",
        fill_value=0
    )
    .reset_index()
)

# Quitar el nombre interno generado para las columnas
pivot.columns.name = None

# ---------------------------------------------------------
# 7. Unir con todas las combinaciones posibles
# ---------------------------------------------------------

resultado = base.merge(
    pivot,
    on=["Anio", "Departamento", "Municipio"],
    how="left"
)

# ---------------------------------------------------------
# 8. Reemplazar delitos ausentes por 0
# ---------------------------------------------------------

columnas_identificacion = [
    "Anio",
    "Departamento",
    "Municipio"
]

columnas_delitos = [
    columna
    for columna in resultado.columns
    if columna not in columnas_identificacion
]

resultado[columnas_delitos] = (
    resultado[columnas_delitos]
    .fillna(0)
    .astype(int)
)

# ---------------------------------------------------------
# 9. Ordenar
# ---------------------------------------------------------

resultado = resultado.sort_values(
    ["Anio", "Departamento", "Municipio"]
).reset_index(drop=True)

# ---------------------------------------------------------
# 10. Validaciones básicas
# ---------------------------------------------------------

print("Filas originales:", len(df))
print("Municipios:", len(municipios))
print("Años:", resultado["Anio"].nunique())
print("Filas esperadas:", 340 * 4)
print("Filas generadas:", len(resultado))
print("\nColumnas finales:")
print(resultado.columns.tolist())

# ---------------------------------------------------------
# 11. Exportar
# ---------------------------------------------------------

resultado.to_csv(
    "denuncias_2022_2025_pivoteado.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nArchivo generado correctamente.")