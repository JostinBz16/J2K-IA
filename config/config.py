
# class Config:
#     # Usa DATABASE_URL como variable de entorno, con un valor por defecto para desarrollo
#     SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://Jxdev:YeNpOuAOlEloDAfllJhcZNqEoJsGmqeJ@postgres.railway.internal:5432/railway')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

class Config:
    # Configuración local para PostgreSQL
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:jxt2004@localhost:5432/j2k_db'
    SQLALCHEMY_DATABASE_URI = 'postgresql://j2kdb_user:LJ9SfwXkLJcPShSa7sW4SwiRsx9G8GVW@dpg-crth5v1u0jms7390tneg-a.oregon-postgres.render.com/j2kdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 