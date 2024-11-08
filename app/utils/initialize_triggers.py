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

    try:
        triggers = [
            # Trigger para INSERT de archivos
            """
            DROP TRIGGER IF EXISTS tr_archivos_x_proyecto_insert
            """,
            """
            CREATE TRIGGER tr_archivos_x_proyecto_insert
            AFTER INSERT ON archivos_x_proyecto
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
                    'archivos_x_proyecto',
                    NEW.id,
                    JSON_OBJECT(),
                    JSON_OBJECT(
                        'proyecto_id', NEW.proyecto_id,
                        'tipos_archivos_id', NEW.tipos_archivos_id,
                        'ruta', NEW.ruta
                    ),
                    NOW()
                );
            END
            """,
            # Trigger para DELETE de archivos
            """
            DROP TRIGGER IF EXISTS tr_archivos_x_proyecto_delete
            """,
            """
            CREATE TRIGGER tr_archivos_x_proyecto_delete
            BEFORE DELETE ON archivos_x_proyecto
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
                    'archivos_x_proyecto',
                    OLD.id,
                    JSON_OBJECT(
                        'proyecto_id', OLD.proyecto_id,
                        'tipos_archivos_id', OLD.tipos_archivos_id,
                        'ruta', OLD.ruta
                    ),
                    JSON_OBJECT(),
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

        print("Triggers de auditoría para archivos inicializados correctamente")

    except Exception as e:
        print(f"Error inicializando triggers de archivos: {str(e)}")

    try:
        triggers = [
            # Trigger para UPDATE de usuarios
            """
            DROP TRIGGER IF EXISTS tr_usuarios_update
            """,
            """
            CREATE TRIGGER tr_usuarios_update 
            AFTER UPDATE ON usuarios
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
                    'usuarios',
                    OLD.id,
                    JSON_OBJECT(
                        'usuario', OLD.usuario,
                        'rol_id', OLD.rol_id,
                        'persona_id', OLD.persona_id,
                        'estado_id', OLD.estado_id
                    ),
                    JSON_OBJECT(
                        'usuario', NEW.usuario,
                        'rol_id', NEW.rol_id,
                        'persona_id', NEW.persona_id,
                        'estado_id', NEW.estado_id
                    ),
                    NOW()
                );
            END
            """,
            # Trigger para DELETE de usuarios (aunque usamos soft delete)
            """
            DROP TRIGGER IF EXISTS tr_usuarios_delete
            """,
            """
            CREATE TRIGGER tr_usuarios_delete
            BEFORE DELETE ON usuarios
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
                    'usuarios',
                    OLD.id,
                    JSON_OBJECT(
                        'usuario', OLD.usuario,
                        'rol_id', OLD.rol_id,
                        'persona_id', OLD.persona_id,
                        'estado_id', OLD.estado_id
                    ),
                    JSON_OBJECT(),
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

        print("Triggers de auditoría para usuarios inicializados correctamente")

    except Exception as e:
        print(f"Error inicializando triggers de usuarios: {str(e)}")

    try:
        triggers = [
            # Trigger para persona UPDATE
            """
            DROP TRIGGER IF EXISTS tr_persona_update
            """,
            """
            CREATE TRIGGER tr_persona_update 
            AFTER UPDATE ON persona
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
                    'persona',
                    OLD.id,
                    JSON_OBJECT(
                        'nombres', OLD.nombres,
                        'apellidos', OLD.apellidos,
                        'rol_id', OLD.rol_id,
                        'estado_id', OLD.estado_id,
                        'telefono', OLD.telefono,
                        'correo', OLD.correo
                    ),
                    JSON_OBJECT(
                        'nombres', NEW.nombres,
                        'apellidos', NEW.apellidos,
                        'rol_id', NEW.rol_id,
                        'estado_id', NEW.estado_id,
                        'telefono', NEW.telefono,
                        'correo', NEW.correo
                    ),
                    NOW()
                );
            END
            """,
            # Trigger para persona DELETE
            """
            DROP TRIGGER IF EXISTS tr_persona_delete
            """,
            """
            CREATE TRIGGER tr_persona_delete
            BEFORE DELETE ON persona
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
                    'persona',
                    OLD.id,
                    JSON_OBJECT(
                        'nombres', OLD.nombres,
                        'apellidos', OLD.apellidos,
                        'rol_id', OLD.rol_id,
                        'estado_id', OLD.estado_id,
                        'telefono', OLD.telefono,
                        'correo', OLD.correo
                    ),
                    JSON_OBJECT(),
                    NOW()
                );
            END
            """,
            # Trigger para profesor DELETE
            """
            DROP TRIGGER IF EXISTS tr_profesor_delete
            """,
            """
            CREATE TRIGGER tr_profesor_delete
            BEFORE DELETE ON profesores
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
                    'profesores',
                    OLD.id,
                    JSON_OBJECT(
                        'persona_id', OLD.persona_id,
                        'matricula', OLD.matricula
                    ),
                    JSON_OBJECT(),
                    NOW()
                );
            END
            """,
            # Trigger para alumno DELETE
            """
            DROP TRIGGER IF EXISTS tr_alumno_delete
            """,
            """
            CREATE TRIGGER tr_alumno_delete
            BEFORE DELETE ON alumnos
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
                    'alumnos',
                    OLD.id,
                    JSON_OBJECT(
                        'persona_id', OLD.persona_id,
                        'matricula', OLD.matricula,
                        'carreras_id', OLD.carreras_id
                    ),
                    JSON_OBJECT(),
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

        print("Triggers de auditoría para personas inicializados correctamente")

    except Exception as e:
        print(f"Error inicializando triggers de personas: {str(e)}")

    try:
        triggers = [
            # Trigger para INSERT en profesor_materia
            """
            DROP TRIGGER IF EXISTS tr_profesor_materia_insert
            """,
            """
            CREATE TRIGGER tr_profesor_materia_insert
            AFTER INSERT ON profesor_materia
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
                    'profesor_materia',
                    NEW.profesor_id,
                    JSON_OBJECT(),
                    JSON_OBJECT(
                        'profesor_id', NEW.profesor_id,
                        'materia_id', NEW.materia_id,
                        'accion', 'asignación'
                    ),
                    NOW()
                );
            END
            """,
            # Trigger para DELETE en profesor_materia
            """
            DROP TRIGGER IF EXISTS tr_profesor_materia_delete
            """,
            """
            CREATE TRIGGER tr_profesor_materia_delete
            BEFORE DELETE ON profesor_materia
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
                    'profesor_materia',
                    OLD.profesor_id,
                    JSON_OBJECT(
                        'profesor_id', OLD.profesor_id,
                        'materia_id', OLD.materia_id,
                        'accion', 'desvinculación'
                    ),
                    JSON_OBJECT(),
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

        print("Triggers de auditoría para asignación de materias inicializados correctamente")

    except Exception as e:
        print(f"Error inicializando triggers de asignación de materias: {str(e)}")

    try:
        triggers = [
            # Trigger para UPDATE en tipos_archivos
            """
            DROP TRIGGER IF EXISTS tr_tipos_archivos_update
            """,
            """
            CREATE TRIGGER tr_tipos_archivos_update 
            AFTER UPDATE ON tipos_archivos
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
                    'tipos_archivos',
                    OLD.id,
                    JSON_OBJECT(
                        'nombre', OLD.nombre
                    ),
                    JSON_OBJECT(
                        'nombre', NEW.nombre
                    ),
                    NOW()
                );
            END
            """,
            # Trigger para DELETE en tipos_archivos
            """
            DROP TRIGGER IF EXISTS tr_tipos_archivos_delete
            """,
            """
            CREATE TRIGGER tr_tipos_archivos_delete
            BEFORE DELETE ON tipos_archivos
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
                    'tipos_archivos',
                    OLD.id,
                    JSON_OBJECT(
                        'nombre', OLD.nombre,
                        'accion', 'eliminación'
                    ),
                    JSON_OBJECT(),
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

        print("Triggers de auditoría para tipos de archivos inicializados correctamente")

    except Exception as e:
        print(f"Error inicializando triggers de tipos de archivos: {str(e)}")