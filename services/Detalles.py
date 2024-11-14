from models.detalle import Detalle
from models.producto import Producto
from models.categoria import Categoria
from utils.db import db


class DetallesService:
    @staticmethod
    def agregar_detalles(producto_id, categoria_id, valoracion, cantidad_valoracion):
        # Validar que los valores no sean nulos o vacíos
        if not producto_id or not categoria_id:
            raise ValueError(
                "El producto y la categoría no pueden ser nulos o indefinidos"
            )

        # Verificar que el producto exista
        producto = Producto.query.get(producto_id)
        if producto is None:
            raise ValueError(f"Producto con ID {producto_id} no encontrado")

        # Verificar que la categoría exista
        categoria = Categoria.query.get(categoria_id)
        if categoria is None:
            raise ValueError(f"Categoría con ID {categoria_id} no encontrada")

        # Si todo es válido, crear el nuevo detalle
        nuevo_detalle = Detalle(
            producto_id=producto_id,
            categoria_id=categoria_id,
            valoracion=valoracion,
            cantida_valoracion=cantidad_valoracion,
        )
        db.session.add(nuevo_detalle)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Revertir cambios en caso de error
            print(f"Error al agregar detalle: {str(e)}")
            raise e  # Vuelve a lanzar la excepción

        return nuevo_detalle

    @staticmethod
    def buscar_detalles_por_id(detalles_id):
        return Detalle.query.get(detalles_id)

    @staticmethod
    def modificar_detalles(
        detalles_id, id_producto, id_categoria, valoracion, cantidad_valoracion
    ):
        # Validar que los valores no sean nulos o vacíos
        if not detalles_id or not id_producto or not id_categoria:
            raise ValueError(
                "El ID del detalle, el ID del producto y la categoría no pueden ser nulos o indefinidos"
            )

        # Verificar que el detalle exista
        detalles = DetallesService.buscar_detalles_por_id(detalles_id)
        if detalles is None:
            raise ValueError(f"Detalles con ID {detalles_id} no encontrados")

        # Actualizar los valores del detalle
        detalles.producto_id = id_producto
        detalles.categoria_id = id_categoria
        detalles.valoracion = valoracion
        detalles.cantida_valoracion = cantidad_valoracion

        detalles = DetallesService.buscar_detalles_por_id(detalles_id)
        if detalles:
            # Verificar que el producto y la categoría asociados existan
            producto = Producto.query.get(detalles.producto_id)
            if producto is None:
                raise ValueError(
                    f"Producto con ID {detalles.producto_id} no encontrado"
                )

            categoria = Categoria.query.get(detalles.categoria_id)
            if categoria is None:
                raise ValueError(
                    f"Categoría con ID {detalles.categoria_id} no encontrada"
                )

            try:
                db.session.commit()
                return detalles
            except Exception as e:
                db.session.rollback()
                print(f"Error al modificar detalles: {str(e)}")
                raise e
        else:
            raise ValueError(f"Detalles con ID {detalles_id} no encontrados")

    @staticmethod
    def eliminar_detalles(detalles_id):
        detalles = DetallesService.buscar_detalles_por_id(detalles_id)
        if detalles:
            db.session.delete(detalles)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error al eliminar detalles: {str(e)}")
                raise e

    @staticmethod
    def buscar_detalles_por_producto(producto_id):
        return Detalle.query.filter_by(producto_id=producto_id).first()

    @staticmethod
    def buscar_detalles_por_categoria(categoria_id):
        return Detalle.query.filter_by(categoria_id=categoria_id).all()
