from models.opinion import Opinion
from utils.db import db


class OpinionService:
    @staticmethod
    def agregar_opinion(contenido, producto_id):
        if not contenido or not producto_id:
            raise ValueError(
                "El contenido y el ID del producto no pueden ser nulos o indefinidos"
            )

        nueva_opinion = Opinion(contenido=contenido, producto_id=producto_id)
        db.session.add(nueva_opinion)
        db.session.commit()
        return nueva_opinion

    @staticmethod
    def buscar_opinion_por_id(opinion_id):
        return Opinion.query.get(opinion_id)

    @staticmethod
    def modificar_opinion(opinion_id, contenido):
        opinion = OpinionService.buscar_opinion_por_id(opinion_id)
        if opinion:
            opinion.contenido = contenido
            db.session.commit()
        return opinion

    @staticmethod
    def eliminar_opinion(opinion_id):
        opinion = OpinionService.buscar_opinion_por_id(opinion_id)
        if opinion:
            db.session.delete(opinion)
            db.session.commit()

    @staticmethod
    def existe_opinion(opinion_id):
        return Opinion.query.get(opinion_id) is not None
