from models.vendedor import Vendedor
from utils.db import db


class VendedorService:
    @staticmethod
    def agregar_vendedor(nombre, es_confiable):
        if not nombre:
            es_confiable = False
            raise ValueError("El nombre del vendedor no puede ser nulo o indefinido")

        nuevo_vendedor = Vendedor(nombre=nombre, confiable=es_confiable)
        db.session.add(nuevo_vendedor)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Revertir cambios en caso de error
            print(
                f"Error al agregar vendedor: {str(e)}"
            )  # Mensaje de error en la consola
            raise e
        return nuevo_vendedor

    @staticmethod
    def buscar_vendedor_por_id(vendedor_id):
        return Vendedor.query.get(vendedor_id)

    @staticmethod
    def modificar_vendedor(vendedor_id, nombre, es_confiable):
        vendedor = VendedorService.buscar_vendedor_por_id(vendedor_id)
        if vendedor:
            vendedor.nombre = nombre
            vendedor.confiable = es_confiable
            db.session.commit()
        return vendedor

    @staticmethod
    def eliminar_vendedor(vendedor_id):
        vendedor = VendedorService.buscar_vendedor_por_id(vendedor_id)
        if vendedor:
            db.session.delete(vendedor)
            db.session.commit()

    @staticmethod
    def existe_vendedor(nombre):
        # En lugar de devolver True/False, devolver el objeto Vendedor o None
        return Vendedor.query.filter_by(nombre=nombre).first()

    @staticmethod
    def obtener_vendedores():
        return Vendedor.query.all()
