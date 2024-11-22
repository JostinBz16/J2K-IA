from utils.db import db


class Detalle(db.Model):
    __tablename__ = "detalles"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(
        db.Integer, db.ForeignKey("productos.id"), nullable=False
    )  # Relación con Producto
    categoria_id = db.Column(
        db.Integer, db.ForeignKey("categorias.id"), nullable=False
    )  # Relación con Categoria
    valoracion = db.Column(db.Float, nullable=True)
    cantida_valoracion = db.Column(db.Integer, nullable=True)
    # comentarios_positivos = db.Column(db.Integer, nullable=False)
    # comentarios_negativos = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        producto_id,
        categoria_id,
        valoracion,
        cantida_valoracion,
    ):
        self.producto_id = producto_id
        self.categoria_id = categoria_id
        self.valoracion = valoracion
        self.cantida_valoracion = cantida_valoracion
