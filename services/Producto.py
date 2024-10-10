from models.producto import Producto
from models.vendedor import Vendedor
from utils.db import db


class ProductoService:
    @staticmethod
    def agregar_producto(
        nombre, precio, image_url, url_producto, valoracion, vendedor_id
    ):
        # Validar que los campos no sean nulos o indefinidos
        if not nombre or not url_producto or not vendedor_id:
            raise ValueError(
                "El nombre, vendedor y enlace no pueden ser nulos o indefinidos"
            )

        # Validar que no exista un producto con el mismo nombre, vendedor y URL
        if ProductoService.existe_producto(nombre, vendedor_id, url_producto):
            raise ValueError("Ya existe un producto con ese nombre, vendedor y enlace")

        nuevo_producto = Producto(
            nombre=nombre,
            precio=precio,
            image_url=image_url,
            url_producto=url_producto,
            valoracion=valoracion,
            vendedor_id=vendedor_id,
        )
        db.session.add(nuevo_producto)
        db.session.commit()
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
            db.session.commit()
        return producto

    @staticmethod
    def eliminar_producto(producto_id):
        producto = ProductoService.buscar_producto_por_id(producto_id)
        if producto:
            db.session.delete(producto)
            db.session.commit()

    @staticmethod
    def existe_producto(nombre, vendedor_id, url_producto):
        return (
            Producto.query.filter(
                (Producto.nombre == nombre)
                & (Producto.vendedor_id == vendedor_id)
                & (Producto.url_producto == url_producto)
            ).first()
            is not None
        )
