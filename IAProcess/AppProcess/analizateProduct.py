from utils.convert import Convert  # Importa desde extensiones
from services.Producto import ProductoService
from services.Vendedor import VendedorService
from services.Opinion import OpinionService
from services.Detalles import DetallesService
from services.Categorias import CategoriaService
from utils.db import db
import traceback


class NoProductsFoundException(Exception):
    """Excepción personalizada para cuando no se encuentran productos"""

    pass


def analizateProductsProcess(products):
    try:
        # Verifica si la lista de productos no está vacía
        if not products or len(products) == 0:
            raise NoProductsFoundException("No se encontraron productos")

        for product in products:
            if (
                product.get("nombre") in [None, ""]
                or product.get("precio") in [None, ""]
                or product.get("calificacion") in [None, ""]
                or product.get("cantidad_calificacion") in [None, ""]
                or product.get("vendedor") in [None, ""]
                or product.get("link") in [None, ""]
                or product.get("categoria") in [None, ""]
                or product.get("valoracion") in [None, ""]
                or product.get("cantidad_valoracion") in [None, ""]
            ):
                continue

            else:
                # Verificar si el vendedor ya existe en la base de datos
                print(f"Procesando vendedor: {product['vendedor']}")
                vendedor = VendedorService.existe_vendedor(product["vendedor"])
                valoracion = (
                    (product["calificacion"])
                    if product["calificacion"] not in [None, "", "null"]
                    else 0.0
                )

                cantidad_valoracion = (
                    (product["cantidad_calificacion"])
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
                        db.session.commit()  # Confirmar cambios
                        print(f"Vendedor agregado: {nombre_vendedor}")

                # Obtener el vendedor actualizado
                new_vendedor = VendedorService.existe_vendedor(product["vendedor"])

                # Verificar si el producto ya existe
                existing_product = ProductoService.existe_producto(
                    product["nombre"],
                    new_vendedor.id,  # Usar el id del vendedor actual
                )

                if existing_product is not None:
                    # Si el producto ya existe, omitir la creación
                    continue
                else:
                    # Convertir los precios y crear un nuevo producto
                    precio_actual = Convert.convert_price_to_float(product["precio"])

                    # Usar el servicio para agregar el nuevo producto
                    ProductoService.agregar_producto(
                        nombre=product["nombre"],
                        descripcion=product["descripcion"],
                        precio=precio_actual,
                        stock=product["stock"],
                        image_url=product["imagen"],
                        url_producto=product["link"],
                        disponible=product["disponible"],
                        vendedor_id=new_vendedor.id,  # Asegurarse de usar el id del vendedor correcto
                    )
                    db.session.commit()  # Confirmar cambios
                    print(f"Producto agregado: {product['nombre']}")

                # Verificar si la categoría ya existe
                categoria_exist = CategoriaService.existe_categoria(
                    product["categoria"]
                )

                if categoria_exist is None:
                    # Si no existe, agregarla
                    CategoriaService.agregar_categoria(nombre=product["categoria"])
                    db.session.commit()  # Confirmar cambios
                    print(f"Categoría agregada: {product['categoria']}")

                    # Obtener la categoría agregada
                    categoria_exist = CategoriaService.existe_categoria(
                        product["categoria"]
                    )

                # Ahora obtenemos el producto recién agregado o verificado
                product_exists = ProductoService.existe_producto(
                    product["nombre"],
                    new_vendedor.id,  # Usar el id del vendedor actual
                )

                # Agregar detalles (relación entre producto y categoría)
                DetallesService.agregar_detalles(
                    producto_id=product_exists.id,
                    categoria_id=categoria_exist.id,  # ID de la categoría encontrada o agregada
                    valoracion=valoracion,
                    cantidad_valoracion=cantidad_valoracion,
                )
                db.session.commit()  # Confirmar cambios
                print(f"Detalles agregados para el producto: {product['nombre']}")

    except Exception as e:
        db.session.rollback()  # Revertir cambios en caso de error
        traceback.print_exc()
        raise e
