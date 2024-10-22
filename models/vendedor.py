from utils.db import db


class Vendedor(db.Model):
    __tablename__ = "vendedores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    confiable = db.Column(db.Boolean, default=False)  # Si el vendedor es confiable

    # Relación uno a muchos con productos
    productos = db.relationship("Producto", backref="vendedor", lazy=True)

    def __init__(self, nombre, confiable=False):
        self.nombre = nombre
        self.confiable = confiable

    def __repr__(self):
        return f"<Vendedor: {self.nombre}, Confiable: {self.confiable}>"
