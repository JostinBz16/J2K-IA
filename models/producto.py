from app import db

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    url_producto = db.Column(db.Text, nullable=True)
    valoracion = db.Column(db.Float, nullable=True)

    # Relación uno a muchos con Opiniones
    opiniones = db.relationship('Opinion', backref='producto', lazy=True)

    def __init__(self, nombre, precio, image_url, url_producto, valoracion):
        self.nombre = nombre
        self.precio = precio
        self.image_url = image_url
        self.url_producto = url_producto
        self.valoracion = valoracion

    def __repr__(self):
        return f"<Producto {self.nombre} - ${self.precio}>"
