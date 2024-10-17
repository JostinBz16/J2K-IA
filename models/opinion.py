from app import db


class Opinion(db.Model):
    __tablename__ = "opiniones"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    contenido = db.Column(db.String(255), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)

    def __init__(self, contenido, producto_id):
        self.contenido = contenido
        self.producto_id = producto_id

    def __repr__(self):
        return f"<Opinion {self.id} para Producto ID {self.producto_id}>"
