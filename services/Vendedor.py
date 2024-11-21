from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from services.Producto import ProductoService
from services.Detalles import DetallesService
from services.Vendedor import VendedorService


def recomendar_productos(descripcion_usuario):
    """
    Función que recomienda productos basados en la descripción proporcionada por el usuario.

    :param descripcion_usuario: Descripción del producto que el usuario busca.
    :return: Lista de productos recomendados con su puntaje de recomendación.
    """
    # 1. Obtener todos los productos desde la base de datos
    productos = (
        ProductoService.buscar_producto_todos()
    )  # Método que obtiene todos los productos
    productos_descripciones = [producto.descripcion for producto in productos]

    # Preprocesamos las descripciones de los productos y la descripción del usuario
    def preprocesar_texto(texto):
        return (
            texto.lower()
        )  # Aquí podrías agregar más preprocesamiento si es necesario

    productos_descripciones = [
        preprocesar_texto(desc) for desc in productos_descripciones
    ]
    descripcion_usuario = preprocesar_texto(descripcion_usuario)

    # 2. Vectorizar las descripciones con TF-IDF
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(
        productos_descripciones + [descripcion_usuario]
    )

    # 3. Calcular la similitud del coseno entre la descripción proporcionada por el usuario y los productos
    cos_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    # 4. Obtener detalles de las valoraciones de los productos
    detalles_productos = DetallesService.buscar_detalles_por_producto_todos()

    # Crear matriz de valoraciones de los productos
    productos_id = [producto.id for producto in productos]
    matriz_valoraciones = np.zeros((len(productos_id), len(productos_id)))

    # Rellenar la matriz de valoraciones
    for i, producto1 in enumerate(productos_id):
        for j, producto2 in enumerate(productos_id):
            if producto1 != producto2:
                valoracion_producto1 = next(
                    (
                        detalle.valoracion
                        for detalle in detalles_productos
                        if detalle.producto_id == producto1
                    ),
                    0,
                )
                valoracion_producto2 = next(
                    (
                        detalle.valoracion
                        for detalle in detalles_productos
                        if detalle.producto_id == producto2
                    ),
                    0,
                )
                matriz_valoraciones[i, j] = valoracion_producto1 * valoracion_producto2

    # Calcular similitud entre productos
    similitudes_productos = cosine_similarity(matriz_valoraciones)

    # 5. Obtener la confiabilidad del vendedor y el precio
    vendedores = VendedorService.buscar_vendedor_todos()
    confiabilidad_vendedor = [1 if vendedor.confiable else 0 for vendedor in vendedores]
    max_precio = max([producto.precio for producto in productos])
    precio_normalizado = [producto.precio / max_precio for producto in productos]

    # 6. Combinación ponderada de todos los factores
    productos_recomendados = []
    for i, producto in enumerate(productos):
        # Normalización de la similitud con la descripción del usuario
        similitud_normalizada = cos_sim[0][i]

        # Obtener la valoración de cada producto y normalizarla
        max_valoraciones = max([detalle.valoracion for detalle in detalles_productos])
        valoraciones_normalizadas = [
            detalle.valoracion / max_valoraciones for detalle in detalles_productos
        ]

        # Puntaje combinado
        puntaje_comb = (
            similitud_normalizada * 0.4  # Similitud con la descripción del usuario
            + valoraciones_normalizadas[i] * 0.3  # Valoración normalizada
            + confiabilidad_vendedor[i] * 0.2  # Confiabilidad del vendedor
            + precio_normalizado[i] * 0.1  # Precio normalizado
        )

        productos_recomendados.append((producto, puntaje_comb))

    # 7. Ordenamos los productos por el puntaje combinado
    productos_recomendados = sorted(
        productos_recomendados, key=lambda x: x[1], reverse=True
    )

    # 8. Devolvemos los productos recomendados (puedes limitar la cantidad si es necesario)
    productos_finales = productos_recomendados[:100]

    # Retornar los productos con su puntaje y detalles
    productos_finales_detalle = [
        {
            "producto": producto.nombre,
            "puntaje": puntaje,
            "precio": producto.precio,
            "valoracion": producto.valoracion,
            "vendedor": producto.vendedor.nombre,
        }
        for producto, puntaje in productos_finales
    ]

    return productos_finales_detalle
