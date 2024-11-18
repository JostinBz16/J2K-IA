from utils.db import db


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    url_producto = db.Column(db.Text, nullable=True)
    # valoracion = db.Column(db.Float, nullable=True)
    disponible = db.Column(db.Boolean, default=False)

    # Clave foránea para asociar el producto con un vendedor
    vendedor_id = db.Column(db.Integer, db.ForeignKey("vendedores.id"), nullable=False)

    # Relación uno a muchos con Opiniones
    opiniones = db.relationship("Opinion", backref="producto", lazy=True)
    detalles = db.relationship("Detalle", backref="producto", lazy=True)

    def __init__(
        self,
        nombre,
        descripcion,
        precio,
        stock,
        image_url,
        url_producto,
        # valoracion,
        disponible,
        vendedor_id,
    ):
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock
        self.image_url = image_url
        self.url_producto = url_producto
        # self.valoracion = valoracion
        self.disponible = disponible
        self.vendedor_id = vendedor_id

    def __repr__(self):
        return f"<Producto {self.nombre} - ${self.precio}>"
