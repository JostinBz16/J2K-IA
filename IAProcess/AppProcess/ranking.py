import spacy
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from services.Producto import ProductoService
from services.Detalles import DetallesService
from services.Vendedor import VendedorService
from IAProcess.AppProcess.recognizeProduct import ProcessInformation
import traceback

# Cargar el modelo en español
nlp = spacy.load("es_core_news_sm")


class CollaborativeRecommendationService:
    def __init__(self):
        self.svd = None
        self.scaler = StandardScaler()
        self.producto_service = ProductoService()
        self.detalles_service = DetallesService()
        self.vendedor_service = VendedorService()
        self.trained = False
        self.user_product_matrix = None
        self.productos_list = None

    def _prepare_training_data(self):
        """Prepara los datos de entrenamiento desde la base de datos."""
        productos = self.producto_service.buscartodos()
        self.productos_list = productos

        # Crear matriz de usuarios-productos
        ratings_data = []

        for producto in productos:
            detalle = self.detalles_service.buscar_detalles_por_producto(producto.id)
            if detalle and detalle.valoracion and detalle.cantida_valoracion:
                for i in range(
                    min(detalle.cantida_valoracion, 10)
                ):  # Limitamos a 10 usuarios por producto
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

        df = pd.DataFrame(ratings_data)
        user_product_matrix = df.pivot(
            index="user_id", columns="product_id", values="rating"
        ).fillna(0)

        return user_product_matrix

    def train_model(self):
        """Entrena el modelo colaborativo."""
        try:
            self.user_product_matrix = self._prepare_training_data()
            n_features = self.user_product_matrix.shape[1]
            n_components = min(100, n_features)
            self.svd = TruncatedSVD(n_components=n_components, random_state=42)
            matrix_scaled = self.scaler.fit_transform(self.user_product_matrix)
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

        vendedor_score = 1.5 if vendedor and vendedor.confiable else 1.0

        if not detalle:
            return vendedor_score

        rating_score = detalle.valoracion if detalle.valoracion else 0
        num_ratings = detalle.cantida_valoracion if detalle.cantida_valoracion else 0
        rating_weight = min(num_ratings / 100, 1)

        return vendedor_score * (rating_score * 0.7 + rating_weight * 0.3)

    def _filter_by_price_range(self, productos, target_price, tolerance=0.3):
        """Filtra productos por rango de precio."""
        if not target_price:
            return productos

        min_price = target_price * (1 - tolerance)
        max_price = target_price * (1 + tolerance)
        return [p for p in productos if min_price <= p.precio <= max_price]

    def _get_user_vector(self, user_id):
        """Obtiene el vector de preferencias del usuario."""
        if user_id in self.user_product_matrix.index:
            return self.user_product_matrix.loc[user_id].values
        return np.mean(self.user_product_matrix.values, axis=0)

    def _predict_ratings(self, user_vector, filtered_product_indices):
        """Predice las valoraciones solo para los productos filtrados."""
        user_vector_scaled = self.scaler.transform(user_vector.reshape(1, -1))
        user_vector_reconstructed = self.svd.inverse_transform(
            self.svd.transform(user_vector_scaled)
        )
        predicted_ratings = self.scaler.inverse_transform(user_vector_reconstructed)[0]
        return {
            idx: predicted_ratings[idx]
            for idx in filtered_product_indices
            if idx < len(predicted_ratings)
        }

    def recommend_products(
        self,
        user_id="default_user",
        target_price=None,
        min_rating=None,
        only_trusted_sellers=False,
        limit=100,
        enunciado_usuario=None,
    ):
        """
        Recomienda productos basados en filtrado colaborativo y criterios adicionales.
        """
        if not self.trained:
            self.train_model()
        if not self.trained:
            return []

        productos = self.productos_list
        productos = [p for p in productos if p.disponible]

        if not productos:
            return []

        if enunciado_usuario:
            product_info = ProcessInformation(enunciado_usuario)
            nombre_producto = product_info["nombre"]
            caracteristicas_deseadas = product_info["caracteristicas"]

            if nombre_producto:
                productos = [
                    p
                    for p in productos
                    if p.descripcion and nombre_producto in p.descripcion.lower()
                ]

            # Filtrar por características
            for categoria, valor in caracteristicas_deseadas.items():
                productos = [
                    p
                    for p in productos
                    if p.descripcion and valor.lower() in p.descripcion.lower()
                ]

        if not productos:
            return []

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

        filtered_product_indices = [
            self.productos_list.index(producto) for producto in productos
        ]

        user_vector = self._get_user_vector(user_id)
        predicted_ratings = self._predict_ratings(user_vector, filtered_product_indices)

        predictions = []
        for producto in productos:
            idx = self.productos_list.index(producto)
            trust_score = self._calculate_trust_score(producto)
            predicted_rating = predicted_ratings.get(idx, 0)
            final_score = predicted_rating * 0.6 + trust_score * 0.4
            predictions.append({"producto": producto, "score": final_score})

        recommended_products = sorted(
            predictions, key=lambda x: x["score"], reverse=True
        )[:limit]

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
def recomendar_productos(user_id="default_user", limit=100, enunciado_usuario=None):
    recommender = CollaborativeRecommendationService()
    return recommender.recommend_products(
        user_id=user_id, limit=limit, enunciado_usuario=enunciado_usuario
    )
