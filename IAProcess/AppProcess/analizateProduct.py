from utils.convert import Convert  # Importa desde extensiones
from services.Producto import ProductoService
from services.Vendedor import VendedorService
from services.Opinion import OpinionService
from services.Detalles import DetallesService
from services.Categorias import CategoriaService
from utils.db import db
from utils.Comentarios import Comentario
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
                    stock=product["stock"],
                    image_url=product["imagen"],
                    url_producto=product["link"],
                    valoracion=valoracion,
                    disponible=product["disponible"],
                    vendedor_id=new_vendedor.id,  # Asegurarse de usar el id del vendedor correcto
                )
                
                existing_categoria = CategoriaService.existe_categoria(
                    product["categorias"]
                )

                if existing_categoria is not None:
                    continue
                else:
                    CategoriaService.agregar_categoria(
                        nombre=product["categorias"]
                    )
                    
                categoria_exist = CategoriaService.existe_categoria(
                    product["categorias"]
                )
                    
            product_exists = ProductoService.existe_producto(
                product["nombre_articulo"],
                new_vendedor.id,  # Usar el id del vendedor actual
            )

            # Ahora puedes agregar las opiniones utilizando el ID del nuevo producto
            # Validar si hay comentarios antes de iterar
            comentarios = product.get("comentarios", [])
            if comentarios:
                positivos, negativos = count_opinions(comentarios)

                # Agregar detalles
                DetallesService.agregar_detalles(
                    producto_id=product_exists.id,
                    categoria_id=categoria_exist.id,  # Categoría por defecto
                    comentarios_positivos=positivos,
                    comentarios_negativos=negativos,
                )

                # Agregar opiniones
                for opinion in comentarios:
                    OpinionService.agregar_opinion(
                        contenido=opinion,
                        producto_id=product_exists.id,
                    )

    except Exception as e:
        db.session.rollback()
        raise e

    def count_opinions(comentarios):
        positivos = 0
        negativos = 0
        for opinion in comentarios:
            result = Comentario.validar_comentario_positivo(opinion)
            if result:
                positivos += 1
            else:
                negativos += 1

    return positivos, negativos
