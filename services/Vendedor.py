from models.vendedor import Vendedor
from utils.db import db


class VendedorService:
    @staticmethod
    def agregar_vendedor(nombre, calificacion, es_confiable):
        if not nombre:
            raise ValueError("El nombre del vendedor no puede ser nulo o indefinido")

        if VendedorService.existe_vendedor(nombre):
            raise ValueError("Ya existe un vendedor con ese nombre")

        nuevo_vendedor = Vendedor(
            nombre=nombre, calificacion=calificacion, es_confiable=es_confiable
        )
        db.session.add(nuevo_vendedor)
        db.session.commit()
        return nuevo_vendedor

    @staticmethod
    def buscar_vendedor_por_id(vendedor_id):
        return Vendedor.query.get(vendedor_id)

    @staticmethod
    def modificar_vendedor(vendedor_id, nombre, calificacion, es_confiable):
        vendedor = VendedorService.buscar_vendedor_por_id(vendedor_id)
        if vendedor:
            vendedor.nombre = nombre
            vendedor.calificacion = calificacion
            vendedor.es_confiable = es_confiable
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
        return Vendedor.query.filter_by(nombre=nombre).first() is not None
