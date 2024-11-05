class Settings:
    # Configuración de la Base de Datos MariaDB
    DB_HOST = "localhost"     #192.168.3.15
    DB_USER = "aabr"
    DB_PASSWORD = "031297.Ale"
    DB_NAME = "repositorio"
    DB_PORT = "3306"  # Puerto por defecto de MariaDB

    # Configuración de la aplicación
    SECRET_KEY = "tu_clave_secreta_muy_larga"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Configuración del servidor
    HOST = "0.0.0.0"
    PORT = 8000

    # URL de conexión a MariaDB
    @property
    def DATABASE_URL(self):
        return f"mysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Crear una instancia de configuración
settings = Settings()