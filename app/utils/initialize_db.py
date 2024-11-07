from sqlalchemy.orm import Session
from ..models import Estado, Rol, Persona, Usuario
from ..database import get_db
import bcrypt
from .initialize_triggers import init_triggers


def init_db():
    db = next(get_db())

    try:
        # Crear estados básicos si no existen
        estados = [
            {"id": 1, "nombre": "Activo"},
            {"id": 2, "nombre": "Inactivo"}
        ]

        for estado in estados:
            db_estado = db.query(Estado).filter(Estado.id == estado["id"]).first()
            if not db_estado:
                db_estado = Estado(**estado)
                db.add(db_estado)

        # Crear roles básicos si no existen
        roles = [
            {"id": 1, "nombre": "Administrador"},
            {"id": 2, "nombre": "Profesor"},
            {"id": 3, "nombre": "Alumno"}
        ]

        for rol in roles:
            db_rol = db.query(Rol).filter(Rol.id == rol["id"]).first()
            if not db_rol:
                db_rol = Rol(**rol)
                db.add(db_rol)

        # Verificar si existe usuario administrador
        admin = db.query(Usuario).filter(Usuario.usuario == "admin").first()
        if not admin:
            # Crear persona para el administrador
            persona_admin = Persona(
                nombres="Administrador",
                apellidos="Del Sistema",
                rol_id=1,  # Administrador
                estado_id=1,  # Activo
                telefono=0,
                correo="admin@sistema.com"
            )
            db.add(persona_admin)
            db.flush()  # Para obtener el ID de la persona

            # Crear usuario administrador
            password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
            admin = Usuario(
                usuario="admin",
                password=password.decode(),
                rol_id=1,  # Administrador
                persona_id=persona_admin.id,
                estado_id=1  # Activo
            )
            db.add(admin)

        db.commit()
        print("Base de datos inicializada correctamente")

        # Inicializar triggers
        init_triggers()

    except Exception as e:
        print(f"Error inicializando la base de datos: {str(e)}")
        db.rollback()
    finally:
        db.close()