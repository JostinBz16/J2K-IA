from models.producto import Producto
from utils.db import db


class ProductoService:
    @staticmethod
    def agregar_producto(
        nombre,
        descripcion,
        precio,
        stock,
        image_url,
        url_producto,
        valoracion,
        disponible,
        vendedor_id,
    ):
        # Validar que los campos no sean nulos o indefinidos
        if not nombre or not url_producto:
            raise ValueError(
                "El nombre, vendedor y enlace no pueden ser nulos o indefinidos"
            )

        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            image_url=image_url,
            url_producto=url_producto,
            valoracion=valoracion,
            disponible=disponible,
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
        producto_id,
        nombre,
        descripcion,
        precio,
        stock,
        image_url,
        url_producto,
        valoracion,
        disponible,
    ):
        producto = ProductoService.buscar_producto_por_id(producto_id)
        if producto:
            producto.nombre = nombre
            producto.descripcion = descripcion
            producto.precio = precio
            producto.stock = stock
            producto.image_url = image_url
            producto.url_producto = url_producto
            producto.valoracion = valoracion
            producto.disponible = disponible
        return producto

    @staticmethod
    def eliminar_producto(producto_id):
        producto = ProductoService.buscar_producto_por_id(producto_id)
        if producto:
            db.session.delete(producto)

    @staticmethod
    def buscar_producto(nombre):
        return Producto.query.filter(nombre=nombre).first()

    @staticmethod
    def existe_producto(nombre, vendedor):
        return Producto.query.filter(
            (Producto.nombre == nombre) and (Producto.vendedor_id == vendedor.id)
        ).first()
