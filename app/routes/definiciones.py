from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import TiposArchivos
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/definiciones")
templates = Jinja2Templates(directory="app/templates")


@router.get("")  # Ruta raíz para /definiciones
@router.get("/")
async def index_definiciones(request: Request):
    return templates.TemplateResponse(
        "definiciones/index.html",
        {"request": request}
    )

@router.get("/tipos-archivos")
async def listar_tipos_archivos(request: Request, db: Session = Depends(get_db)):
    tipos = db.query(TiposArchivos).all()
    return templates.TemplateResponse(
        "definiciones/tipos_archivos.html",
        {
            "request": request,
            "tipos": tipos,
            "mensaje_error": request.query_params.get("error"),
            "mensaje_exito": request.query_params.get("exito")
        }
    )

@router.post("/tipos-archivos")
async def crear_tipo_archivo(
    nombre: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        tipo_existente = db.query(TiposArchivos).filter(TiposArchivos.nombre == nombre).first()
        if tipo_existente:
            return RedirectResponse(
                url="/definiciones/tipos-archivos?error=Ya existe un tipo de archivo con ese nombre",
                status_code=303
            )

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
    tipo_id: int,
    nombre: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        tipo = db.query(TiposArchivos).filter(TiposArchivos.id == tipo_id).first()
        if not tipo:
            return RedirectResponse(
                url="/definiciones/tipos-archivos?error=Tipo de archivo no encontrado",
                status_code=303
            )

        # Verificar si ya existe otro tipo con el mismo nombre
        tipo_existente = db.query(TiposArchivos).filter(
            TiposArchivos.nombre == nombre,
            TiposArchivos.id != tipo_id
        ).first()
        if tipo_existente:
            return RedirectResponse(
                url="/definiciones/tipos-archivos?error=Ya existe un tipo de archivo con ese nombre",
                status_code=303
            )

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