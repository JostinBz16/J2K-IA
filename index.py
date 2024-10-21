from app import app
from utils.db import db  # Importa desde extensiones

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")

if __name__ == "__main__":
    app.run(debug=True)
