from sqlalchemy import text
from ..database import engine


def init_triggers():
    try:
        triggers = [
            """
            DROP TRIGGER IF EXISTS tr_facultades_update
            """,
            """
            CREATE TRIGGER tr_facultades_update 
            AFTER UPDATE ON facultades
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'facultades',
                    OLD.id,
                    JSON_OBJECT(
                        'codigo', OLD.codigo,
                        'nombre', OLD.nombre,
                        'estado_id', OLD.estado_id
                    ),
                    JSON_OBJECT(
                        'codigo', NEW.codigo,
                        'nombre', NEW.nombre,
                        'estado_id', NEW.estado_id
                    ),
                    NOW()
                );
            END
            """,
            """
            DROP TRIGGER IF EXISTS tr_facultades_delete
            """,
            """
            CREATE TRIGGER tr_facultades_delete
            BEFORE DELETE ON facultades
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'facultades',
                    OLD.id,
                    JSON_OBJECT(
                        'codigo', OLD.codigo,
                        'nombre', OLD.nombre,
                        'estado_id', OLD.estado_id
                    ),
                    JSON_OBJECT(),
                    NOW()
                );
            END
            """,
            """
            DROP TRIGGER IF EXISTS tr_carreras_update
            """,
            """
            CREATE TRIGGER tr_carreras_update
            AFTER UPDATE ON carreras
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'carreras',
                    OLD.id,
                    JSON_OBJECT(
                        'codigo', OLD.codigo,
                        'nombre', OLD.nombre,
                        'facultades_id', OLD.facultades_id,
                        'estado_id', OLD.estado_id
                    ),
                    JSON_OBJECT(
                        'codigo', NEW.codigo,
                        'nombre', NEW.nombre,
                        'facultades_id', NEW.facultades_id,
                        'estado_id', NEW.estado_id
                    ),
                    NOW()
                );
            END
            """,
            """
            DROP TRIGGER IF EXISTS tr_carreras_delete
            """,
            """
            CREATE TRIGGER tr_carreras_delete
            BEFORE DELETE ON carreras
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'carreras',
                    OLD.id,
                    JSON_OBJECT(
                        'codigo', OLD.codigo,
                        'nombre', OLD.nombre,
                        'facultades_id', OLD.facultades_id,
                        'estado_id', OLD.estado_id
                    ),
                    JSON_OBJECT(),
                    NOW()
                );
            END
            """,
            """
            DROP TRIGGER IF EXISTS tr_materias_update
            """,
            """
            CREATE TRIGGER tr_materias_update
            AFTER UPDATE ON materias
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'materias',
                    OLD.id,
                    JSON_OBJECT(
                        'codigo', OLD.codigo,
                        'nombre', OLD.nombre,
                        'carreras_id', OLD.carreras_id,
                        'curso', OLD.curso,
                        'estado_id', OLD.estado_id
                    ),
                    JSON_OBJECT(
                        'codigo', NEW.codigo,
                        'nombre', NEW.nombre,
                        'carreras_id', NEW.carreras_id,
                        'curso', NEW.curso,
                        'estado_id', NEW.estado_id
                    ),
                    NOW()
                );
            END
            """,
            """
            DROP TRIGGER IF EXISTS tr_materias_delete
            """,
            """
            CREATE TRIGGER tr_materias_delete
            BEFORE DELETE ON materias
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'materias',
                    OLD.id,
                    JSON_OBJECT(
                        'codigo', OLD.codigo,
                        'nombre', OLD.nombre,
                        'carreras_id', OLD.carreras_id,
                        'curso', OLD.curso,
                        'estado_id', OLD.estado_id
                    ),
                    JSON_OBJECT(),
                    NOW()
                );
            END
            """
        ]

        # Ejecutar cada trigger por separado
        with engine.connect() as conn:
            # Establecer valor por defecto para @user_id
            conn.execute(text("SET @user_id = 0"))

            for trigger in triggers:
                if trigger.strip():
                    conn.execute(text(trigger))

            conn.commit()

        print("Triggers de auditoría para gestion acedemica inicializados correctamente")

    except Exception as e:
        print(f"Error inicializando la base de datos: {str(e)}")

    try:
        triggers = [
            # Trigger para proyecto UPDATE
            """
            DROP TRIGGER IF EXISTS tr_proyecto_update
            """,
            """
            CREATE TRIGGER tr_proyecto_update 
            AFTER UPDATE ON proyecto
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'proyecto',
                    OLD.id,
                    JSON_OBJECT(
                        'nombre', OLD.nombre,
                        'descripcion', OLD.descripcion,
                        'estado_id', OLD.estado_id
                    ),
                    JSON_OBJECT(
                        'nombre', NEW.nombre,
                        'descripcion', NEW.descripcion,
                        'estado_id', NEW.estado_id
                    ),
                    NOW()
                );
            END
            """,
            # Trigger para proyecto DELETE
            """
            DROP TRIGGER IF EXISTS tr_proyecto_delete
            """,
            """
            CREATE TRIGGER tr_proyecto_delete
            BEFORE DELETE ON proyecto
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'proyecto',
                    OLD.id,
                    JSON_OBJECT(
                        'nombre', OLD.nombre,
                        'descripcion', OLD.descripcion,
                        'estado_id', OLD.estado_id,
                        'profesor_id', OLD.profesor_id
                    ),
                    JSON_OBJECT(),
                    NOW()
                );
            END
            """,
            # Trigger para proyecto_x_materia DELETE
            """
            DROP TRIGGER IF EXISTS tr_proyecto_x_materia_delete
            """,
            """
            CREATE TRIGGER tr_proyecto_x_materia_delete
            BEFORE DELETE ON proyecto_x_materia
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'proyecto_x_materia',
                    OLD.id,
                    JSON_OBJECT(
                        'proyecto_id', OLD.proyecto_id,
                        'materias_id', OLD.materias_id,
                        'profesores_id', OLD.profesores_id
                    ),
                    JSON_OBJECT(),
                    NOW()
                );
            END
            """,
            # Trigger para proyecto_x_materia INSERT
            """
            DROP TRIGGER IF EXISTS tr_proyecto_x_materia_insert
            """,
            """
            CREATE TRIGGER tr_proyecto_x_materia_insert
            AFTER INSERT ON proyecto_x_materia
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'proyecto_x_materia',
                    NEW.id,
                    JSON_OBJECT(),
                    JSON_OBJECT(
                        'proyecto_id', NEW.proyecto_id,
                        'materias_id', NEW.materias_id,
                        'profesores_id', NEW.profesores_id
                    ),
                    NOW()
                );
            END
            """,
            # Trigger para alumnos_x_proyecto DELETE
            """
            DROP TRIGGER IF EXISTS tr_alumnos_x_proyecto_delete
            """,
            """
            CREATE TRIGGER tr_alumnos_x_proyecto_delete
            BEFORE DELETE ON alumnos_x_proyecto
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'alumnos_x_proyecto',
                    OLD.id,
                    JSON_OBJECT(
                        'proyecto_id', OLD.proyecto_id,
                        'alumnos_id', OLD.alumnos_id
                    ),
                    JSON_OBJECT(),
                    NOW()
                );
            END
            """,
            # Trigger para alumnos_x_proyecto INSERT
            """
            DROP TRIGGER IF EXISTS tr_alumnos_x_proyecto_insert
            """,
            """
            CREATE TRIGGER tr_alumnos_x_proyecto_insert
            AFTER INSERT ON alumnos_x_proyecto
            FOR EACH ROW
            BEGIN
                INSERT INTO auditoria (
                    usuario,
                    tabla,
                    id_registro,
                    valor_anterior,
                    valor_nuevo,
                    fecha
                ) VALUES (
                    @user_id,
                    'alumnos_x_proyecto',
                    NEW.id,
                    JSON_OBJECT(),
                    JSON_OBJECT(
                        'proyecto_id', NEW.proyecto_id,
                        'alumnos_id', NEW.alumnos_id
                    ),
                    NOW()
                );
            END
            """
        ]

        # Ejecutar cada trigger
        with engine.connect() as conn:
            conn.execute(text("SET @user_id = 0"))

            for trigger in triggers:
                if trigger.strip():
                    conn.execute(text(trigger))

            conn.commit()

        print("Triggers de auditoría para proyectos inicializados correctamente")

    except Exception as e:
        print(f"Error inicializando triggers de proyectos: {str(e)}")