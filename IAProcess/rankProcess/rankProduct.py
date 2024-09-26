import pandas as pd
import json
import chardet

def rankProduct(jsonFile):
    # Detectar la codificación del archivo
    with open(jsonFile, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    # Cargar el JSON desde el archivo usando la codificación detectada
    try:
        with open(jsonFile, 'r', encoding=encoding) as f:
            data = json.load(f)
            print("Datos cargados correctamente:", data)  # Verificar si los datos se cargan correctamente
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        return []

    # Verificar si hay datos para procesar
    if not data:
        print("No se encontraron datos en el archivo JSON")
        return []

    # Normalizar el JSON para convertirlo en un DataFrame
    df = pd.json_normalize(data)
    print("DataFrame después de normalización:\n", df)  # Imprimir el DataFrame para verificar

    # Verificar si las columnas necesarias están presentes
    required_columns = ['precio', 'valoracion']
    if not all(col in df.columns for col in required_columns):
        print(f"Faltan columnas requeridas. Columnas presentes: {df.columns}")
        return []

    # Limpiar y convertir los valores de precio y valoracion
    try:
        df['precio'] = df['precio'].astype(str).str.replace(r'[\$,]', '', regex=True).astype(float)
        df['valoracion'] = df['valoracion'].astype(str).str.extract(r'(\d+\.\d+)').astype(float)
        print("DataFrame después de limpiar 'precio' y 'valoracion':\n", df[['precio', 'valoracion']])  # Verificar limpieza
    except Exception as e:
        print(f"Error al procesar 'precio' o 'valoracion': {e}")
        return []

    # Realizar el ranking: ponderamos con mayor peso la valoración y menor el precio
    df['ranking_score'] = df['valoracion'] / df['precio']

    # Ordenar por el ranking
    df_ranked = df.sort_values(by='ranking_score', ascending=False)
    print("DataFrame después del ranking:\n", df_ranked[['precio', 'valoracion', 'ranking_score']])  # Verificar el ranking

    # Convertir el DataFrame a una lista de diccionarios
    productos_rankeados = df_ranked.to_dict(orient='records')

    return productos_rankeados
