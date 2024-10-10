from app import db


class Vendedor(db.Model):
    __tablename__ = "vendedores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    calificacion = db.Column(db.Float, nullable=True)  # Calificación del vendedor
    confiable = db.Column(db.Boolean, default=False)  # Si el vendedor es confiable

    # Relación uno a muchos con productos
    productos = db.relationship("Producto", backref="vendedor", lazy=True)

    def __init__(self, nombre, descripcion=None, calificacion=None, confiable=False):
        self.nombre = nombre
        self.descripcion = descripcion
        self.calificacion = calificacion
        self.confiable = confiable

    def __repr__(self):
        return f"<Vendedor {self.nombre} - Calificación: {self.calificacion} - Confiable: {self.confiable}>"
