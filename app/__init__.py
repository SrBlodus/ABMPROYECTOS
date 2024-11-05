from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import Base, engine
from .models import *
from .utils.initialize_db import init_db
import os

# Crear la instancia de FastAPI
app = FastAPI(
    title="Sistema de Gestión de Proyectos Académicos",
    description="Sistema para gestionar proyectos académicos",
    version="1.0.0"
)

# Crear directorio de archivos si no existe
os.makedirs("archivos", exist_ok=True)

# Montar directorio de archivos
app.mount("/archivos", StaticFiles(directory="archivos"), name="archivos")

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar datos básicos
init_db()

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Importar routers
from .routes import (
    personas_router,
    academic_router,
    proyectos_router,
    archivos_router,
    definiciones_router,
    profesor_materias_router
)

# Incluir routers
app.include_router(personas_router)
app.include_router(academic_router)
app.include_router(proyectos_router)
app.include_router(archivos_router)
app.include_router(definiciones_router)
app.include_router(profesor_materias_router)

# Ruta principal que lleva al dashboard
@app.get("/")
@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})