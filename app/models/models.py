from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

# Tabla intermedia para la relación profesor-materia
profesor_materia = Table('profesor_materia',
    Base.metadata,
    Column('profesor_id', Integer, ForeignKey('profesores.id'), primary_key=True),
    Column('materia_id', Integer, ForeignKey('materias.id'), primary_key=True)
)

class Estado(Base):
    __tablename__ = "estado"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(45), nullable=False)

class Rol(Base):
    __tablename__ = "rol"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(45), nullable=False)

class Persona(Base):
    __tablename__ = "persona"
    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    rol_id = Column(Integer, ForeignKey("rol.id"))
    estado_id = Column(Integer, ForeignKey("estado.id"))
    telefono = Column(Integer, nullable=False)
    correo = Column(String(60), nullable=False)

    rol = relationship("Rol")
    estado = relationship("Estado")
    usuario = relationship("Usuario", back_populates="persona")
    profesor = relationship("Profesor", back_populates="persona")
    alumno = relationship("Alumno", back_populates="persona")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(45), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Aumentamos el tamaño para el hash
    rol_id = Column(Integer, ForeignKey("rol.id"))
    persona_id = Column(Integer, ForeignKey("persona.id"))
    estado_id = Column(Integer, ForeignKey("estado.id"))

    rol = relationship("Rol")
    persona = relationship("Persona", back_populates="usuario")
    estado = relationship("Estado")

    @property
    def es_admin(self):
        return self.rol_id == 1

    @property
    def es_profesor(self):
        return self.rol_id == 2

    @property
    def es_alumno(self):
        return self.rol_id == 3

class Facultad(Base):
    __tablename__ = "facultades"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), nullable=False, unique=True)
    nombre = Column(String(200), nullable=False)
    estado_id = Column(Integer, ForeignKey("estado.id"))

    estado = relationship("Estado")
    carreras = relationship("Carrera", back_populates="facultad")

class Carrera(Base):
    __tablename__ = "carreras"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    facultades_id = Column(Integer, ForeignKey("facultades.id"))
    estado_id = Column(Integer, ForeignKey("estado.id"))

    facultad = relationship("Facultad", back_populates="carreras")
    estado = relationship("Estado")
    materias = relationship("Materia", back_populates="carrera")
    alumnos = relationship("Alumno", back_populates="carrera")

class Materia(Base):
    __tablename__ = "materias"
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), nullable=False, unique=True)
    nombre = Column(String(45), nullable=False)
    carreras_id = Column(Integer, ForeignKey("carreras.id"))
    curso = Column(Integer, nullable=False)
    estado_id = Column(Integer, ForeignKey("estado.id"))

    carrera = relationship("Carrera", back_populates="materias")
    estado = relationship("Estado")
    proyectos = relationship("ProyectoXMateria", back_populates="materia")
    profesores = relationship("Profesor", secondary=profesor_materia, back_populates="materias")

class Profesor(Base):
    __tablename__ = "profesores"
    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("persona.id"))
    matricula = Column(String(45), nullable=False)

    persona = relationship("Persona", back_populates="profesor")
    proyectos = relationship("Proyecto", back_populates="profesor")  # Añadir esta línea
    proyectos_materias = relationship("ProyectoXMateria", back_populates="profesor")
    materias = relationship("Materia", secondary=profesor_materia, back_populates="profesores")

class Alumno(Base):
    __tablename__ = "alumnos"
    id = Column(Integer, primary_key=True, index=True)
    carreras_id = Column(Integer, ForeignKey("carreras.id"))
    persona_id = Column(Integer, ForeignKey("persona.id"))
    matricula = Column(String(45), nullable=False)

    persona = relationship("Persona", back_populates="alumno")
    carrera = relationship("Carrera", back_populates="alumnos")
    proyectos = relationship("AlumnosXProyecto", back_populates="alumno")

class Proyecto(Base):
    __tablename__ = "proyecto"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    estado_id = Column(Integer, ForeignKey("estado.id"))
    descripcion = Column(Text)
    profesor_id = Column(Integer, ForeignKey("profesores.id"))  # Añadir esta línea

    estado = relationship("Estado")
    profesor = relationship("Profesor", back_populates="proyectos")  # Actualizar esta línea
    materias = relationship("ProyectoXMateria", back_populates="proyecto")
    alumnos = relationship("AlumnosXProyecto", back_populates="proyecto")
    archivos = relationship("ArchivosXProyecto", back_populates="proyecto")

class ProyectoXMateria(Base):
    __tablename__ = "proyecto_x_materia"
    id = Column(Integer, primary_key=True, index=True)
    materias_id = Column(Integer, ForeignKey("materias.id"))
    proyecto_id = Column(Integer, ForeignKey("proyecto.id"))
    profesores_id = Column(Integer, ForeignKey("profesores.id"))

    materia = relationship("Materia", back_populates="proyectos")
    proyecto = relationship("Proyecto", back_populates="materias")
    profesor = relationship("Profesor", back_populates="proyectos_materias")

class AlumnosXProyecto(Base):
    __tablename__ = "alumnos_x_proyecto"
    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyecto.id"))
    alumnos_id = Column(Integer, ForeignKey("alumnos.id"))

    proyecto = relationship("Proyecto", back_populates="alumnos")
    alumno = relationship("Alumno", back_populates="proyectos")

class TiposArchivos(Base):
    __tablename__ = "tipos_archivos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(45), nullable=False)

    archivos = relationship("ArchivosXProyecto", back_populates="tipo_archivo")

class ArchivosXProyecto(Base):
    __tablename__ = "archivos_x_proyecto"
    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyecto.id"))
    tipos_archivos_id = Column(Integer, ForeignKey("tipos_archivos.id"))
    ruta = Column(String(255), nullable=False)

    proyecto = relationship("Proyecto", back_populates="archivos")
    tipo_archivo = relationship("TiposArchivos", back_populates="archivos")


class Auditoria(Base):
    __tablename__ = "auditoria"
    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(Integer, nullable=False)
    tabla = Column(String(45), nullable=False)
    id_registro = Column(Integer, nullable=False)
    valor_anterior = Column(Text, nullable=False)
    valor_nuevo = Column(Text, nullable=False)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)