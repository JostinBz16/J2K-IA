from app import db


class Detalles(db.Model):
    __tablename__ = "detalles"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    comentarios_positivos = db.Column(db.Integer, nullable=False)
    comentarios_negativos = db.Column(db.Integer, nullable=False)

    def __init__(
        self, producto_id, categoria_id, comentarios_positivos, comentarios_negativos
    ):
        self.producto_id = producto_id
        self.categoria_id = categoria_id
        self.comentarios_positivos = comentarios_positivos
        self.comentarios_negativos = comentarios_negativos
