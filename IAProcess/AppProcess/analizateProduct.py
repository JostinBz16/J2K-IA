from utils.convert import Convert  # Importa desde extensiones
from services.Producto import ProductoService
from services.Vendedor import VendedorService
from services.Opinion import OpinionService
from utils.db import db
import os


class NoProductsFoundException(Exception):
    """Excepción personalizada para cuando no se encuentran productos"""

    pass


def analizateProductsProcess(products):
    try:
        # Verifica si la lista de productos no está vacía
        if not products or len(products) == 0:
            raise NoProductsFoundException("No se encontraron productos")

        for product in products:
            # Verificar si el vendedor ya existe en la base de datos
            vendedor = VendedorService.existe_vendedor(product["vendedor"])
            valoracion = (
                float(product["calificacion"])
                if product["calificacion"] not in [None, "", "null"]
                else 0.0
            )
            if vendedor is None:
                # Validar el valor de "confiable" y asignar False si no está presente o es inválido
                es_confiable = product.get("confiable", False)
                nombre_vendedor = product["vendedor"]

                # Agregar el vendedor
                VendedorService.agregar_vendedor(nombre_vendedor, es_confiable)

            new_vendedor = VendedorService.existe_vendedor(product["vendedor"])
            # Verificar si el producto ya existe usando el id correcto
            existing_product = ProductoService.existe_producto(
                product["nombre_articulo"],
                new_vendedor.id,  # Usar el id del vendedor actual
            )

            if existing_product is not None:
                continue
                # ProductoService.modificar_producto(
                #     existing_product.id,
                #     nombre=product["nombre_articulo"],
                #     descripcion=product["descripcion"],
                #     precio=Convert.convert_price_to_float(
                #         product["precio"]
                #     ),
                #     image_url=product["imagen"],
                #     url_producto=product["link"],
                #     valoracion=valoracion,
                #     vendedor_id=new_vendedor.id,  # Asegurarse de usar el id del vendedor correcto
                # )
            else:
                # Convertir los precios y crear un nuevo producto
                precio_actual = Convert.convert_price_to_float(product["precio"])

                # Usar el servicio para agregar el nuevo producto
                ProductoService.agregar_producto(
                    nombre=product["nombre_articulo"],
                    descripcion=product["descripcion"],
                    precio=precio_actual,
                    image_url=product["imagen"],
                    url_producto=product["link"],
                    valoracion=valoracion,
                    vendedor_id=new_vendedor.id,  # Asegurarse de usar el id del vendedor correcto
                )

            product_exists = ProductoService.existe_producto(
                product["nombre_articulo"],
                new_vendedor.id,  # Usar el id del vendedor actual
            )

            # Ahora puedes agregar las opiniones utilizando el ID del nuevo producto
            # Validar si hay comentarios antes de iterar
            comentarios = product.get("comentarios", [])
            if comentarios and isinstance(comentarios, list):
                # Agregar opiniones si existen comentarios válidos
                for comentario in comentarios:
                    OpinionService.agregar_opinion(
                        contenido=comentario,
                        producto_id=product_exists.id,  # Usa el ID del producto agregado
                    )

                # Commit de todas las adiciones al final de la iteración
    except Exception as e:
        db.session.rollback()
        raise e
