from models.categoria import Categoria
from utils.db import db


class CategoriaService:
    @staticmethod
    def agregar_categoria(nombre):
        # Validar que el nombre no sea nulo o indefinido
        if not nombre:
            raise ValueError("El nombre de la categoría no puede ser nulo o indefinido")

        nueva_categoria = Categoria(nombre=nombre)
        db.session.add(nueva_categoria)

        # Intenta hacer commit y captura excepciones
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Revertir cambios en caso de error
            print(
                f"Error al agregar categoría: {str(e)}"
            )  # Mensaje de error en consola
            raise e  # Vuelve a lanzar la excepción

        return nueva_categoria

    @staticmethod
    def buscar_categoria_por_id(categoria_id):
        return Categoria.query.get(categoria_id)

    @staticmethod
    def buscar_categoria_por_nombre(nombre_categoria):
        categoria = Categoria.query.filter_by(nombre=nombre_categoria).first()
        return categoria

    @staticmethod
    def modificar_categoria(categoria_id, nombre):
        categoria = CategoriaService.buscar_categoria_por_id(categoria_id)
        if categoria:
            categoria.nombre = nombre
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error al modificar categoría: {str(e)}")
                raise e
        return categoria

    @staticmethod
    def eliminar_categoria(categoria_id):
        categoria = CategoriaService.buscar_categoria_por_id(categoria_id)
        if categoria:
            db.session.delete(categoria)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error al eliminar categoría: {str(e)}")
                raise e

    @staticmethod
    def existe_categoria(nombre):
        return Categoria.query.filter_by(nombre=nombre).first()
