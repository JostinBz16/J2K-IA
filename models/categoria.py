from app import db


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    nombre = db.Column(db.Text, nullable=False)

    def __init__(self, nombre):
        self.nombre = nombre

    def __repr__(self):
        return f"<{self.id} - {self.nombre}>"
