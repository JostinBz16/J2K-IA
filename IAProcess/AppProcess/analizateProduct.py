from utils.convert import Convert  # Importa desde extensiones
from services.Producto import ProductoService
from services.Vendedor import VendedorService
from services.Opinion import OpinionService
from services.Detalles import DetallesService
from services.Categorias import CategoriaService
from utils.db import db
from utils.Comentarios import Comentario
import traceback


class NoProductsFoundException(Exception):
    """Excepción personalizada para cuando no se encuentran productos"""

    pass


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


def analizateProductsProcess(products):
    try:
        # Verifica si la lista de productos no está vacía
        if not products or len(products) == 0:
            raise NoProductsFoundException("No se encontraron productos")

        for product in products:
            if (
                (product["nombre"] is [None, ""])
                or (product["precio"] is [None, ""])
                or (product["calificacion"] is [None, ""])
                or (product["cantidad_calificacion"] is [None, ""])
                or (product["vendedor"] is [None, ""])
                or (product["link"] is [None, ""])
            ):
                continue
            else:
                # Verificar si el vendedor ya existe en la base de datos
                print(product["vendedor"])
                vendedor = VendedorService.existe_vendedor(product["vendedor"])
                valoracion = (
                    float(product["calificacion"])
                    if product["calificacion"] not in [None, "", "null"]
                    else 0.0
                )

                cantidad_valoracion = (
                    int(product["cantidad_calificacion"])
                    if product["cantidad_calificacion"] not in [None, "", "null"]
                    else 0
                )

                if product["vendedor"] == "" or product["vendedor"] is None:
                    continue
                else:
                    if vendedor is None:
                        # Validar el valor de "confiable" y asignar False si no está presente o es inválido
                        es_confiable = product.get("confiable", False)
                        nombre_vendedor = product["vendedor"]

                        # Agregar el vendedor
                        VendedorService.agregar_vendedor(nombre_vendedor, es_confiable)

                # Obtener el vendedor actualizado
                new_vendedor = VendedorService.existe_vendedor(product["vendedor"])

                # Verificar si el producto ya existe
                existing_product = ProductoService.existe_producto(
                    product["nombre_articulo"],
                    new_vendedor.id,  # Usar el id del vendedor actual
                )

                if existing_product is not None:
                    # Si el producto ya existe, puedes omitir la creación
                    continue
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
                        disponible=product["disponible"],
                        vendedor_id=new_vendedor.id,  # Asegurarse de usar el id del vendedor correcto
                    )

                # Verificar si la categoría ya existe
                categoria_exist = CategoriaService.existe_categoria(
                    product["categoria"]
                )

                if categoria_exist is None:
                    # Si no existe, agregarla
                    CategoriaService.agregar_categoria(nombre=product["categoria"])
                    # Obtener la categoría agregada
                    categoria_exist = CategoriaService.existe_categoria(
                        product["categoria"]
                    )

                # Ahora obtenemos el producto recién agregado o verificado
                product_exists = ProductoService.existe_producto(
                    product["nombre_articulo"],
                    new_vendedor.id,  # Usar el id del vendedor actual
                )

                # Validar si hay comentarios antes de iterar
                # comentarios = product.get("comentarios", [])
                # if comentarios:
                #     positivos, negativos = count_opinions(comentarios)

                # Agregar detalles (relación entre producto y categoría)
                DetallesService.agregar_detalles(
                    producto_id=product_exists.id,
                    categoria_id=categoria_exist.id,  # ID de la categoría encontrada o agregada
                    valoracion=valoracion,
                    cantidad_valoracion=cantidad_valoracion,
                )

                # Agregar opiniones
                # for opinion in comentarios:
                #     OpinionService.agregar_opinion(
                #         contenido=opinion,
                #         producto_id=product_exists.id,  # Relacionar con el producto
                #     )

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e
