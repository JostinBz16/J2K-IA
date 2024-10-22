import pandas as pd
import numpy as np
import json


def rankProduct(data):
    # Cargar los datos desde la variable JSON

    productos_df = pd.json_normalize(data)

    # Limpiar datos (eliminar filas con valores nulos en precio, ventas o calidad)
    productos_df = productos_df.dropna(subset=["precio", "ventas", "calidad"])

    # Normalizar el precio y las ventas entre 0 y 1
    productos_df["precio_normalizado"] = (
        productos_df["precio"] - productos_df["precio"].min()
    ) / (productos_df["precio"].max() - productos_df["precio"].min())
    productos_df["ventas_normalizadas"] = (
        productos_df["ventas"] - productos_df["ventas"].min()
    ) / (productos_df["ventas"].max() - productos_df["ventas"].min())

    # Calcular el ranking basado en calidad, ventas y precio (donde menor precio es mejor)
    productos_df["ranking"] = (
        productos_df["calidad"] * 0.5
        + productos_df["ventas_normalizadas"] * 0.3
        - productos_df["precio_normalizado"] * 0.2
    )

    # Ordenar por el ranking de mayor a menor
    productos_rankeados = productos_df.sort_values(by="ranking", ascending=False)

    # Obtener los mejores 100 productos (en este caso, solo hay 3)
    mejores_100_productos = productos_rankeados.head(100)

    # Convertir a JSON para devolver en una API o guardarlo en un archivo
    mejores_100_json_str = mejores_100_productos[["id", "nombre", "ranking"]].to_json(
        orient="records"
    )

    # Convertir el string JSON a un diccionario de Python
    mejores_100_dict = json.loads(mejores_100_json_str)

    return mejores_100_dict

    # Llamada a la función
    resultado_dict = rankProduct()
    print(resultado_dict)  # Ahora es un diccionario de Python
