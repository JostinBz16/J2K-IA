import spacy
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from services.Producto import ProductoService
from services.Detalles import DetallesService
from services.Vendedor import VendedorService
import traceback

# Cargar el modelo en español
nlp = spacy.load("es_core_news_sm")


class CollaborativeRecommendationService:
    def __init__(self):
        self.producto_service = ProductoService()
        self.detalles_service = DetallesService()
        self.vendedor_service = VendedorService()

    def _calculate_similarity_score(self, enunciado, descripcion):
        """Calcula la similitud semántica entre el enunciado del usuario y la descripción del producto."""
        doc1 = nlp(enunciado)
        doc2 = nlp(descripcion)
        return doc1.similarity(doc2)

    def _calculate_trust_score(self, producto):
        """Calcula el puntaje de confianza basado en el vendedor y las valoraciones."""
        detalle = self.detalles_service.buscar_detalles_por_producto(producto.id)
        vendedor = self.vendedor_service.buscar_vendedor_por_id(producto.vendedor_id)

        vendedor_score = 1.5 if vendedor and vendedor.confiable else 1.0

        if not detalle:
            return vendedor_score

        rating_score = detalle.valoracion if detalle.valoracion else 0
        num_ratings = detalle.cantida_valoracion if detalle.cantida_valoracion else 0
        rating_weight = min(num_ratings / 100, 1)

        return vendedor_score * (rating_score * 0.7 + rating_weight * 0.3)

    def recommend_products(
        self,
        enunciado_usuario,
        min_rating=None,
        only_trusted_sellers=True,
        limit=100,
    ):
        """
        Recomienda productos basados en:
        - Similitud con el enunciado del usuario.
        - Disponibilidad del producto.
        - Confianza del vendedor.
        - Valoraciones del producto.
        """
        try:
            # Obtener productos disponibles
            productos = self.producto_service.buscartodos()
            productos = [p for p in productos if p.disponible]

            if not productos:
                return []

            # Filtrar por vendedores confiables si se especifica
            if only_trusted_sellers:
                productos = [
                    p
                    for p in productos
                    if self.vendedor_service.buscar_vendedor_por_id(p.vendedor_id)
                    and self.vendedor_service.buscar_vendedor_por_id(
                        p.vendedor_id
                    ).confiable
                ]

            if not productos:
                return []

            # Calcular similitud, valoración y score final
            recomendaciones = []
            for producto in productos:
                detalle = self.detalles_service.buscar_detalles_por_producto(
                    producto.id
                )
                valoracion = detalle.valoracion if detalle else 0
                num_valoraciones = detalle.cantida_valoracion if detalle else 0

                # Filtrar por valor mínimo de rating
                if min_rating and valoracion < min_rating:
                    continue

                similitud = (
                    self._calculate_similarity_score(
                        enunciado_usuario, producto.descripcion
                    )
                    if producto.descripcion
                    else 0
                )
                confianza = self._calculate_trust_score(producto)
                score_final = (
                    similitud * 0.5
                    + confianza * 0.3
                    + (valoracion * 0.2 + min(num_valoraciones / 100, 0.1))
                )

                recomendaciones.append(
                    {
                        "producto": producto,
                        "score": score_final,
                        "similarity": similitud,
                        "trust_score": confianza,
                        "valoracion": valoracion,
                        "num_valoraciones": num_valoraciones,
                    }
                )

            # Ordenar las recomendaciones por el puntaje calculado
            recomendaciones = sorted(
                recomendaciones, key=lambda x: x["score"], reverse=True
            )

            # Retornar la lista de productos recomendados
            return [
                {
                    "id": item["producto"].id,
                    "nombre": item["producto"].nombre,
                    "precio": item["producto"].precio,
                    "descripcion": item["producto"].descripcion,
                    "image_url": item["producto"].image_url,
                    "url_producto": item["producto"].url_producto,
                    "vendedor": self.vendedor_service.buscar_vendedor_por_id(
                        item["producto"].vendedor_id
                    ).nombre,
                    "valoracion": item["valoracion"],
                    "num_valoraciones": item["num_valoraciones"],
                    "similarity": item["similarity"],
                    "trust_score": item["trust_score"],
                    "score": item["score"],
                }
                for item in recomendaciones[:limit]
            ]
        except Exception as e:
            traceback.print_exc()
            print(f"Error al recomendar productos: {e}")
            return []


# Función para usar en la ruta de Flask
def recomendar_productos(enunciado_usuario, limit=100):
    recommender = CollaborativeRecommendationService()
    return recommender.recommend_products(
        enunciado_usuario=enunciado_usuario, limit=limit
    )
