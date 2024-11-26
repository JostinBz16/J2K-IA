# from transformers import pipeline


# class Comentario:

#     @staticmethod
#     def validar_comentario_positivo(comentario):
#         if not isinstance(comentario, str):
#             raise ValueError("El comentario debe ser una cadena de texto")

#         if len(comentario) == 0:
#             raise ValueError("El comentario no puede estar vacío")

#         # Cargar el pipeline para análisis de sentimientos con un modelo multilingüe
#         sentiment_pipeline = pipeline(
#             "sentiment-analysis",
#             model="nlptown/bert-base-multilingual-uncased-sentiment",
#         )

#         resultado = sentiment_pipeline(comentario)
#         # print(f"Sentimiento: {resultado}\n")

#         # Obtener el número de estrellas y decidir si es positivo o negativo
#         label = resultado[0]["label"]
#         num_estrellas = int(label.split()[0])  # Extraer el número de estrellas

#         # Consideramos 4 o 5 estrellas como positivo
#         if num_estrellas >= 3.5:
#             return True
#         else:
#             return False
