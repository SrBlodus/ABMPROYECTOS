from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import TiposArchivos, Usuario
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from .auth import get_current_user
from typing import Optional
from sqlalchemy import text


router = APIRouter(prefix="/definiciones")
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


@router.get("")  # Ruta raíz para /definiciones
@router.get("/")
async def index_definiciones(
        request: Request,
        current_user: Usuario = Depends(verify_admin)
):
    return templates.TemplateResponse(
        "definiciones/index.html",
        {
            "request": request,
            "user": current_user
        }
    )

def set_audit_user(db: Session, user_id: int):
    try:
        db.execute(text("SET @user_id = :user_id"), {"user_id": user_id})
    except Exception as e:
        print(f"Error al establecer usuario de auditoría: {str(e)}")


@router.get("/tipos-archivos")
async def listar_tipos_archivos(
        request: Request,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        tipos = db.query(TiposArchivos).all()
        return templates.TemplateResponse(
            "definiciones/tipos_archivos.html",
            {
                "request": request,
                "tipos": tipos,
                "mensaje_error": request.query_params.get("error"),
                "mensaje_exito": request.query_params.get("exito"),
                "user": current_user
            }
        )
    except Exception as e:
        return RedirectResponse(
            url="/definiciones/tipos-archivos?error=" + str(e),
            status_code=303
        )


@router.post("/tipos-archivos")
async def crear_tipo_archivo(
        request: Request,
        nombre: str = Form(...),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        # Verificar si ya existe
        tipo_existente = db.query(TiposArchivos).filter(TiposArchivos.nombre == nombre).first()
        if tipo_existente:
            return RedirectResponse(
                url="/definiciones/tipos-archivos?error=Ya existe un tipo de archivo con ese nombre",
                status_code=303
            )

        # Crear nuevo tipo
        nuevo_tipo = TiposArchivos(nombre=nombre)
        db.add(nuevo_tipo)
        db.commit()

        return RedirectResponse(
            url="/definiciones/tipos-archivos?exito=Tipo de archivo creado exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/definiciones/tipos-archivos?error={str(e)}",
            status_code=303
        )

@router.post("/tipos-archivos/{tipo_id}/editar")
async def editar_tipo_archivo(
    request: Request,
    tipo_id: int,
    nombre: str = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        # Establecer usuario para auditoría
        set_audit_user(db, current_user.id)

        # Verificar si existe
        tipo = db.query(TiposArchivos).filter(TiposArchivos.id == tipo_id).first()
        if not tipo:
            return RedirectResponse(
                url="/definiciones/tipos-archivos?error=Tipo de archivo no encontrado",
                status_code=303
            )

        # Verificar nombre duplicado
        tipo_existente = db.query(TiposArchivos).filter(
            TiposArchivos.nombre == nombre,
            TiposArchivos.id != tipo_id
        ).first()
        if tipo_existente:
            return RedirectResponse(
                url="/definiciones/tipos-archivos?error=Ya existe un tipo de archivo con ese nombre",
                status_code=303
            )

        # Actualizar y guardar (será auditado por el trigger)
        tipo.nombre = nombre
        db.commit()

        return RedirectResponse(
            url="/definiciones/tipos-archivos?exito=Tipo de archivo actualizado exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/definiciones/tipos-archivos?error={str(e)}",
            status_code=303
        )

@router.post("/tipos-archivos/{tipo_id}/eliminar")
async def eliminar_tipo_archivo(
    request: Request,
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        # Establecer usuario para auditoría
        set_audit_user(db, current_user.id)

        tipo = db.query(TiposArchivos).filter(TiposArchivos.id == tipo_id).first()
        if not tipo:
            return RedirectResponse(
                url="/definiciones/tipos-archivos?error=Tipo de archivo no encontrado",
                status_code=303
            )

        # Verificar si hay archivos usando este tipo
        if tipo.archivos:
            return RedirectResponse(
                url="/definiciones/tipos-archivos?error=No se puede eliminar porque hay archivos usando este tipo",
                status_code=303
            )

        # Eliminar (será auditado por el trigger)
        db.delete(tipo)
        db.commit()

        return RedirectResponse(
            url="/definiciones/tipos-archivos?exito=Tipo de archivo eliminado exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/definiciones/tipos-archivos?error={str(e)}",
            status_code=303
        )