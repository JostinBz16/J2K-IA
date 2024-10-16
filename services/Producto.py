from models.producto import Producto
from models.vendedor import Vendedor
from utils.db import db


class ProductoService:
    @staticmethod
    def agregar_producto(
        nombre, precio, image_url, url_producto, valoracion, vendedor_id
    ):
        # Validar que los campos no sean nulos o indefinidos
        if not nombre or not url_producto:
            raise ValueError(
                "El nombre, vendedor y enlace no pueden ser nulos o indefinidos"
            )

        nuevo_producto = Producto(
            nombre=nombre,
            precio=precio,
            image_url=image_url,
            url_producto=url_producto,
            valoracion=valoracion,
            vendedor_id=vendedor_id,
        )
        db.session.add(nuevo_producto)
        # Intenta hacer commit y captura excepciones
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Revertir cambios en caso de error
            print(
                f"Error al agregar producto: {str(e)}"
            )  # Mensaje de error en la consola
            raise e  # Vuelve a lanzar la excepción

        return nuevo_producto

    @staticmethod
    def buscar_producto_por_id(producto_id):
        return Producto.query.get(producto_id)

    def buscar_producto_por_nombre(nombre_producto):
        producto = Producto.query.filter_by(nombre=nombre_producto).first()
        return producto

    @staticmethod
    def modificar_producto(
        producto_id, nombre, precio, image_url, url_producto, valoracion
    ):
        producto = ProductoService.buscar_producto_por_id(producto_id)
        if producto:
            producto.nombre = nombre
            producto.precio = precio
            producto.image_url = image_url
            producto.url_producto = url_producto
            producto.valoracion = valoracion
        return producto

    @staticmethod
    def eliminar_producto(producto_id):
        producto = ProductoService.buscar_producto_por_id(producto_id)
        if producto:
            db.session.delete(producto)

    @staticmethod
    def existe_producto(nombre, vendedor):
        return Producto.query.filter(
            (Producto.nombre == nombre) and (Producto.vendedor_id == vendedor.id)
        ).first()
