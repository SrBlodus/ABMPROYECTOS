from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Auditoria, Usuario
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from .auth import get_current_user
from typing import Optional
from sqlalchemy import desc

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Función para verificar si el usuario es administrador
async def verify_admin(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[Usuario]:
    user = await get_current_user(request, db)
    if not user or user.rol_id != 1:  # Asumiendo que rol_id 1 es administrador
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    return user

@router.get("/auditoria")
async def ver_auditoria(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        # Obtener parámetros de filtro
        tabla = request.query_params.get("tabla")
        fecha_desde = request.query_params.get("fecha_desde")
        fecha_hasta = request.query_params.get("fecha_hasta")

        # Query base
        query = db.query(Auditoria).order_by(desc(Auditoria.fecha))

        # Aplicar filtros si existen
        if tabla:
            query = query.filter(Auditoria.tabla == tabla)
        if fecha_desde:
            query = query.filter(Auditoria.fecha >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Auditoria.fecha <= fecha_hasta)

        # Obtener registros de auditoría
        registros = query.all()

        # Obtener tablas únicas para el filtro
        tablas_unicas = db.query(Auditoria.tabla).distinct().all()
        tablas = [t[0] for t in tablas_unicas]

        return templates.TemplateResponse(
            "auditoria/index.html",
            {
                "request": request,
                "registros": registros,
                "tablas": tablas,
                "tabla_seleccionada": tabla,
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta,
                "user": current_user
            }
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/dashboard?error={str(e)}",
            status_code=303
        )