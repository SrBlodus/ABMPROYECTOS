from .personas import router as personas_router
from .academic import router as academic_router
from .proyectos import router as proyectos_router
from .archivos import router as archivos_router
from .definiciones import router as definiciones_router
from .profesor_materias import router as profesor_materias_router

__all__ = [
    'personas_router',
    'academic_router',
    'proyectos_router',
    'archivos_router',
    'definiciones_router',
    'profesor_materias_router'
]