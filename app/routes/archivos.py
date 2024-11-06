from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import (
    Proyecto, ArchivosXProyecto, TiposArchivos, Usuario,
    Profesor, Alumno, AlumnosXProyecto
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse
from .auth import get_current_user
import os
import shutil
from typing import Optional
from datetime import datetime

router = APIRouter(
    prefix="/proyectos/{proyecto_id}/archivos",
    tags=["archivos"]
)

templates = Jinja2Templates(directory="app/templates")


async def can_manage_files(
        request: Request,
        proyecto_id: int,
        db: Session = Depends(get_db)
) -> Optional[Usuario]:
    user = await get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=403, detail="No autorizado")

    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Verificar si es profesor del proyecto
    if user.rol_id == 2:
        profesor = db.query(Profesor).filter(
            Profesor.persona_id == user.persona_id
        ).first()
        if profesor and profesor.id == proyecto.profesor_id:
            return user

    # Verificar si es alumno del proyecto
    elif user.rol_id == 3:
        alumno = db.query(Alumno).filter(
            Alumno.persona_id == user.persona_id
        ).first()
        if alumno:
            vinculacion = db.query(AlumnosXProyecto).filter(
                AlumnosXProyecto.proyecto_id == proyecto_id,
                AlumnosXProyecto.alumnos_id == alumno.id
            ).first()
            if vinculacion:
                return user

    raise HTTPException(
        status_code=403,
        detail="No tienes permisos para gestionar archivos en este proyecto"
    )


@router.get("")
async def ver_archivos(
        request: Request,
        proyecto_id: int,
        db: Session = Depends(get_db)
):
    try:
        user = await get_current_user(request, db)
        proyecto = db.query(Proyecto).options(
            joinedload(Proyecto.archivos).joinedload(ArchivosXProyecto.tipo_archivo)
        ).filter(Proyecto.id == proyecto_id).first()

        if not proyecto:
            return RedirectResponse(
                url="/proyectos?error=Proyecto no encontrado",
                status_code=303
            )

        # Verificar permisos
        can_edit = False
        try:
            await can_manage_files(request, proyecto_id, db)
            can_edit = True
        except:
            pass

        tipos_archivos = db.query(TiposArchivos).all()

        return templates.TemplateResponse(
            "archivos/index.html",
            {
                "request": request,
                "proyecto": proyecto,
                "tipos_archivos": tipos_archivos,
                "user": user,
                "can_edit": can_edit
            }
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}?error={str(e)}",
            status_code=303
        )


@router.post("/subir")
async def subir_archivo(
        proyecto_id: int,
        archivo: UploadFile = File(...),
        tipo_archivo_id: int = Form(...),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(can_manage_files)
):
    try:
        # Verificar el tipo de archivo
        tipo_archivo = db.query(TiposArchivos).filter(TiposArchivos.id == tipo_archivo_id).first()
        if not tipo_archivo:
            raise HTTPException(status_code=400, detail="Tipo de archivo no válido")

        # Crear directorio si no existe
        proyecto_dir = f"archivos/proyecto_{proyecto_id}"
        os.makedirs(proyecto_dir, exist_ok=True)

        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{archivo.filename}"
        file_path = os.path.join(proyecto_dir, filename)

        # Guardar el archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)

        # Crear registro en la base de datos
        nuevo_archivo = ArchivosXProyecto(
            proyecto_id=proyecto_id,
            tipos_archivos_id=tipo_archivo_id,
            ruta=file_path
        )
        db.add(nuevo_archivo)
        db.commit()

        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/archivos?exito=Archivo subido exitosamente",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/archivos?error={str(e)}",
            status_code=303
        )


@router.get("/{archivo_id}/descargar")
async def descargar_archivo(
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
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        if not os.path.exists(archivo.ruta):
            raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")

        return FileResponse(
            archivo.ruta,
            filename=os.path.basename(archivo.ruta),
            media_type="application/octet-stream"
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/archivos?error={str(e)}",
            status_code=303
        )


@router.post("/{archivo_id}/eliminar")
async def eliminar_archivo(
        request: Request,
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

        # Verificar permisos
        await can_manage_files(request, proyecto_id, db)

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
        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/archivos?error={str(e)}",
            status_code=303
        )