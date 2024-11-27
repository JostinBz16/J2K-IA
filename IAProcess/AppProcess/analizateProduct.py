from utils.convert import Convert  # Importa desde extensiones
from services.Producto import ProductoService
from services.Vendedor import VendedorService
from services.Detalles import DetallesService
from utils.db import db
import math
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
            # Usar .get() para evitar KeyError
            nombre = product.get("nombre")
            precio = product.get("precio")
            calificacion = product.get("calificacion")
            cantidad_calificacion = product.get("cantidad_calificacion")
            vendedor = product.get("vendedor")
            link = product.get("link")

            try:
                calificacion = int(calificacion) if calificacion is not None else None
                cantidad_calificacion = (
                    float(cantidad_calificacion)
                    if cantidad_calificacion is not None
                    else None
                )
            except ValueError:
                calificacion = None
                cantidad_calificacion = None

            # Validaciones de los valores
            if (
                nombre is None
                or precio is None
                or calificacion is None
                or math.isnan(calificacion)
                or cantidad_calificacion is None
                or math.isnan(cantidad_calificacion)
                or vendedor is None
                or link is None
            ):
                continue

            # Verificar si el vendedor ya existe en la base de datos
            vendedor_obj = VendedorService.existe_vendedor(vendedor)
            valoracion = calificacion if calificacion not in [None, "", "null"] else 0.0
            cantidad_valoracion = (
                cantidad_calificacion
                if cantidad_calificacion not in [None, "", "null"]
                else 0
            )

            if not vendedor:
                continue
            else:
                if vendedor_obj is None:
                    es_confiable = product.get("confiable", False)
                    VendedorService.agregar_vendedor(vendedor, es_confiable)

            # Obtener el vendedor actualizado
            new_vendedor = VendedorService.existe_vendedor(vendedor)

            # Verificar si el producto ya existe
            existing_product = ProductoService.existe_producto(
                nombre,
                new_vendedor.id,  # Usar el id del vendedor actual
            )

            if existing_product is not None:
                continue
            else:
                precio_actual = Convert.convert_price_to_float(precio)
                ProductoService.agregar_producto(
                    nombre=nombre,
                    descripcion=product.get("descripcion"),
                    precio=precio_actual,
                    stock=product.get("stock"),
                    image_url=product.get("imagen"),
                    url_producto=link,
                    disponible=product.get("disponible", True),
                    vendedor_id=new_vendedor.id,
                )

            # Obtener el producto recién agregado
            product_exists = ProductoService.existe_producto(nombre, new_vendedor.id)

            # Agregar detalles del producto
            DetallesService.agregar_detalles(
                producto_id=product_exists.id,
                valoracion=valoracion,
                cantidad_valoracion=cantidad_valoracion,
            )

        # Confirmar transacciones
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        raise e
