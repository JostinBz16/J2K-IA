from app import app
from utils.db import db  # Importa desde extensiones
from models.categoria import Categoria
from models.detalle import Detalle
from models.producto import Producto
from models.vendedor import Vendedor
from models.opinion import Opinion

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")

if __name__ == "__main__":
    app.run(debug=True)
