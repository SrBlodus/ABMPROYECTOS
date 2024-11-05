from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import TiposArchivos, ArchivosXProyecto, Proyecto
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import os
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# Ruta para ver archivos de un proyecto específico
@router.get("/proyectos/{proyecto_id}/archivos")
async def ver_archivos_proyecto(request: Request, proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    archivos = db.query(ArchivosXProyecto).filter(
        ArchivosXProyecto.proyecto_id == proyecto_id
    ).options(joinedload(ArchivosXProyecto.tipo_archivo)).all()

    tipos_archivos = db.query(TiposArchivos).all()

    return templates.TemplateResponse(
        "archivos/proyecto_archivos.html",
        {
            "request": request,
            "proyecto": proyecto,
            "archivos": archivos,
            "tipos_archivos": tipos_archivos,
            "mensaje_error": request.query_params.get("error"),
            "mensaje_exito": request.query_params.get("exito")
        }
    )


# Ruta para subir un archivo a un proyecto
@router.post("/proyectos/{proyecto_id}/archivos/subir")
async def subir_archivo(
        proyecto_id: int,
        archivo: UploadFile = File(...),
        tipo_archivo_id: int = Form(...),
        db: Session = Depends(get_db)
):
    try:
        proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
        if not proyecto:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")

        # Crear directorio para el proyecto si no existe
        directorio = f"archivos/proyecto_{proyecto_id}"
        os.makedirs(directorio, exist_ok=True)

        # Guardar el archivo con su nombre original
        ruta_archivo = f"{directorio}/{archivo.filename}"

        # Guardar el archivo
        with open(ruta_archivo, "wb") as buffer:
            content = await archivo.read()
            buffer.write(content)

        # Guardar registro en la base de datos usando ruta relativa
        nuevo_archivo = ArchivosXProyecto(
            proyecto_id=proyecto_id,
            tipos_archivos_id=tipo_archivo_id,
            ruta=ruta_archivo  # La ruta incluirá 'archivos/proyecto_X/nombre_archivo'
        )
        db.add(nuevo_archivo)
        db.commit()

        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/archivos?exito=Archivo subido exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/archivos?error={str(e)}",
            status_code=303
        )


# Ruta para eliminar un archivo
@router.post("/proyectos/{proyecto_id}/archivos/{archivo_id}/eliminar")
async def eliminar_archivo(
        proyecto_id: int,
        archivo_id: int,
        db: Session = Depends(get_db)
):
    try:
        archivo = db.query(ArchivosXProyecto).filter(
            ArchivosXProyecto.id == archivo_id,
            ArchivosXProyecto.proyecto_id == proyecto_id
        ).first()

        if not archivo:
            return RedirectResponse(
                url=f"/proyectos/{proyecto_id}/archivos?error=Archivo no encontrado",
                status_code=303
            )

        # Eliminar archivo físico
        if os.path.exists(archivo.ruta):
            os.remove(archivo.ruta)

        # Eliminar registro de la base de datos
        db.delete(archivo)
        db.commit()

        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/archivos?exito=Archivo eliminado exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/archivos?error={str(e)}",
            status_code=303
        )

# Configuración - Tipos de Archivos
@router.get("/configuracion/tipos-archivos")
async def configuracion_tipos_archivos(request: Request, db: Session = Depends(get_db)):
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


@router.post("/configuracion/tipos-archivos")
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