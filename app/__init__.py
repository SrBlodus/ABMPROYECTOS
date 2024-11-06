from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import *
from .utils.initialize_db import init_db
from .routes.auth import login_required, get_current_user
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


# Middleware para verificar autenticación
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Rutas que no requieren autenticación
    public_paths = ["/login", "/static", "/archivos", "/docs", "/openapi.json"]

    # Verificar si es una ruta pública
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    # Obtener el token
    token = request.cookies.get("access_token")

    # Si no hay token y no es la ruta de login, redirigir al login
    if not token and request.url.path != "/login":
        return RedirectResponse(url="/login", status_code=303)

    # Procesar la solicitud
    response = await call_next(request)

    return response


# Importar routers
from .routes import (
    personas_router,
    academic_router,
    proyectos_router,
    archivos_router,
    definiciones_router,
    profesor_materias_router,
    usuarios_router,
    auth_router
)

# Incluir routers
app.include_router(auth_router)  # El router de auth debe ser el primero
app.include_router(personas_router)
app.include_router(academic_router)
app.include_router(proyectos_router)
app.include_router(archivos_router)
app.include_router(definiciones_router)
app.include_router(profesor_materias_router)
app.include_router(usuarios_router)


# Ruta principal que redirecciona al dashboard
@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")


# Ruta del dashboard protegida
@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        # Intentar obtener el usuario actual
        current_user = await get_current_user(request, db)
        if not current_user:
            return RedirectResponse(url="/login", status_code=303)

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": current_user
            }
        )
    except Exception as e:
        print(f"Error en dashboard: {str(e)}")  # Para debugging
        return RedirectResponse(url="/login", status_code=303)

# Agregar el manejador de excepciones aquí
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 403:
        return templates.TemplateResponse(
            "errors/403.html",
            {"request": request},
            status_code=403
        )
    raise exc