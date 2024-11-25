import sys
import os
import traceback

# Agrega la carpeta raíz del proyecto al `sys.path`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from typing import List, Dict
from services.Producto import ProductoService
from services.Detalles import DetallesService
from services.Vendedor import VendedorService


class CollaborativeRecommendationService:
    def __init__(self):
        self.svd = TruncatedSVD(n_components=100, random_state=42)
        self.scaler = StandardScaler()
        self.producto_service = ProductoService
        self.detalles_service = DetallesService
        self.vendedor_service = VendedorService
        self.trained = False
        self.user_product_matrix = None
        self.productos_list = None

    def _prepare_training_data(self):
        """Prepara los datos de entrenamiento desde la base de datos."""
        # Obtener todos los productos y sus detalles
        productos = self.producto_service.buscartodos()
        self.productos_list = productos

        # Crear matriz de usuarios-productos
        ratings_data = []

        for producto in productos:
            detalle = self.detalles_service.buscar_detalles_por_producto(producto.id)
            if detalle and detalle.valoracion and detalle.cantida_valoracion:
                # Crear múltiples entradas basadas en la valoración promedio
                for i in range(
                    min(detalle.cantida_valoracion, 10)
                ):  # Limitamos a 10 usuarios por producto
                    # Añadimos algo de variación a las valoraciones para simular usuarios reales
                    variation = np.random.normal(0, 0.5)
                    rating = max(1, min(5, detalle.valoracion + variation))
                    ratings_data.append(
                        {
                            "user_id": f"user_{producto.id}_{i}",
                            "product_id": producto.id,
                            "rating": rating,
                        }
                    )

        if not ratings_data:
            raise ValueError(
                "No hay suficientes datos de valoraciones para entrenar el modelo"
            )

        # Convertir a DataFrame
        df = pd.DataFrame(ratings_data)

        # Crear matriz de usuarios-productos
        user_product_matrix = df.pivot(
            index="user_id", columns="product_id", values="rating"
        ).fillna(0)

        return user_product_matrix

    def train_model(self):
        """Entrena el modelo colaborativo."""
        try:
            self.user_product_matrix = self._prepare_training_data()

            # Normalizar los datos
            matrix_scaled = self.scaler.fit_transform(self.user_product_matrix)

            # Aplicar SVD
            self.svd.fit(matrix_scaled)

            self.trained = True
        except Exception as e:
            traceback.print_exc()
            print(f"Error al entrenar el modelo: {e}")
            self.trained = False

    def _calculate_trust_score(self, producto) -> float:
        """Calcula el puntaje de confianza basado en el vendedor y las valoraciones."""
        detalle = self.detalles_service.buscar_detalles_por_producto(producto.id)
        vendedor = self.vendedor_service.buscar_vendedor_por_id(producto.vendedor_id)

        # Factor base de confianza del vendedor
        vendedor_score = 1.5 if vendedor and vendedor.confiable else 1.0

        if not detalle:
            return vendedor_score

        # Normalización de valoraciones
        rating_score = detalle.valoracion if detalle.valoracion else 0
        num_ratings = detalle.cantida_valoracion if detalle.cantida_valoracion else 0

        # Factor de confianza basado en cantidad de valoraciones
        rating_weight = min(num_ratings / 100, 1)  # Normalizar a máximo 1

        return vendedor_score * (rating_score * 0.7 + rating_weight * 0.3)

    def _filter_by_price_range(
        self, productos: List, target_price: float, tolerance: float = 0.3
    ) -> List:
        """Filtra productos por rango de precio."""
        if not target_price:
            return productos

        min_price = target_price * (1 - tolerance)
        max_price = target_price * (1 + tolerance)
        return [p for p in productos if min_price <= p.precio <= max_price]

    def _get_user_vector(self, user_id: str):
        """Obtiene el vector de preferencias del usuario."""
        if user_id in self.user_product_matrix.index:
            return self.user_product_matrix.loc[user_id].values
        # Si es un nuevo usuario, devolver un vector promedio
        return np.mean(self.user_product_matrix.values, axis=0)

    def _predict_ratings(self, user_vector):
        """Predice las valoraciones para todos los productos."""
        # Normalizar el vector de usuario
        user_vector_scaled = self.scaler.transform(user_vector.reshape(1, -1))

        # Proyectar en el espacio latente y reconstruir
        user_vector_reconstructed = self.svd.inverse_transform(
            self.svd.transform(user_vector_scaled)
        )

        # Desnormalizar
        return self.scaler.inverse_transform(user_vector_reconstructed)[0]

    def recommend_products(
        self,
        user_id: str = "default_user",
        target_price: float = None,
        min_rating: float = None,
        only_trusted_sellers: bool = False,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Recomienda productos basados en filtrado colaborativo y criterios adicionales.
        """
        if not self.trained:
            self.train_model()

        if not self.trained:
            return []

        # Obtener todos los productos disponibles
        productos = self.productos_list
        productos = [p for p in productos if p.disponible]

        if not productos:
            return []

        # Aplicar filtros iniciales
        if only_trusted_sellers:
            productos = [
                p
                for p in productos
                if self.vendedor_service.buscar_vendedor_por_id(p.vendedor_id).confiable
            ]

        if min_rating:
            productos = [
                p
                for p in productos
                if self.detalles_service.buscar_detalles_por_producto(p.id)
                and self.detalles_service.buscar_detalles_por_producto(p.id).valoracion
                >= min_rating
            ]

        if target_price:
            productos = self._filter_by_price_range(productos, target_price)

        if not productos:
            return []

        # Obtener predicciones para el usuario
        user_vector = self._get_user_vector(user_id)
        predicted_ratings = self._predict_ratings(user_vector)

        # Calcular scores finales
        predictions = []
        for idx, producto in enumerate(self.productos_list):
            if producto in productos:  # Solo procesar productos que pasaron los filtros
                trust_score = self._calculate_trust_score(producto)
                predicted_rating = predicted_ratings[idx]

                # Combinar predicción con score de confianza
                final_score = predicted_rating * 0.6 + trust_score * 0.4

                predictions.append({"producto": producto, "score": final_score})

        # Ordenar por puntaje final
        recommended_products = sorted(
            predictions, key=lambda x: x["score"], reverse=True
        )[:limit]

        # Formatear resultados
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
                "valoracion": (
                    self.detalles_service.buscar_detalles_por_producto(
                        item["producto"].id
                    ).valoracion
                    if self.detalles_service.buscar_detalles_por_producto(
                        item["producto"].id
                    )
                    else None
                ),
                "num_valoraciones": (
                    self.detalles_service.buscar_detalles_por_producto(
                        item["producto"].id
                    ).cantida_valoracion
                    if self.detalles_service.buscar_detalles_por_producto(
                        item["producto"].id
                    )
                    else None
                ),
                "score": item["score"],
            }
            for item in recommended_products
        ]


# Función para usar en la ruta de Flask
def recomendar_productos(user_id: str = "default_user", limit: int = 100) -> List[Dict]:
    """
    Función para usar directamente en las rutas de Flask.
    """
    recommender = CollaborativeRecommendationService()
    return recommender.recommend_products(user_id=user_id, limit=limit)
