from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session, joinedload

from .. import ArchivosXProyecto, TiposArchivos
from ..database import get_db
from ..models import (
    Proyecto, Estado, ProyectoXMateria, AlumnosXProyecto,
    Materia, Alumno, Profesor, Usuario
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import List, Optional
from datetime import datetime
from .auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


async def get_user_permissions(user: Usuario, proyecto_id: int, db: Session) -> dict:
    """
    Retorna un diccionario con los permisos del usuario para un proyecto específico.
    """
    permissions = {
        "can_edit": False,
        "can_delete": False,
        "is_vinculado": False
    }

    if not user:
        return permissions

    # Si es profesor
    if user.rol_id == 2:
        profesor = db.query(Profesor).filter(
            Profesor.persona_id == user.persona_id
        ).first()

        if profesor:
            proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
            if proyecto and proyecto.profesor_id == profesor.id:
                permissions["can_edit"] = True
                permissions["can_delete"] = True

    # Si es alumno
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
                permissions["can_edit"] = True
                permissions["is_vinculado"] = True

    return permissions

def set_audit_user(db: Session, user_id: int):
    try:
        db.execute(text("SET @user_id = :user_id"), {"user_id": user_id})
    except Exception as e:
        print(f"Error al establecer usuario de auditoría: {str(e)}")



@router.get("/proyectos")
async def listar_proyectos(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        user = await get_current_user(request, db)
        proyectos = db.query(Proyecto).options(
            joinedload(Proyecto.estado),
            joinedload(Proyecto.profesor).joinedload(Profesor.persona),
            joinedload(Proyecto.materias).joinedload(ProyectoXMateria.materia),
            joinedload(Proyecto.alumnos).joinedload(AlumnosXProyecto.alumno)
        ).all()

        # Si el usuario es alumno, marcar sus proyectos
        user_proyectos = set()
        if user and user.rol_id == 3:
            alumno = db.query(Alumno).filter(Alumno.persona_id == user.persona_id).first()
            if alumno:
                vinculaciones = db.query(AlumnosXProyecto).filter(
                    AlumnosXProyecto.alumnos_id == alumno.id
                ).all()
                user_proyectos = {v.proyecto_id for v in vinculaciones}

        return templates.TemplateResponse(
            "proyectos/index.html",
            {
                "request": request,
                "proyectos": proyectos,
                "user": user,
                "user_proyectos": user_proyectos,
                "mensaje_error": request.query_params.get("error"),
                "mensaje_exito": request.query_params.get("exito")
            }
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/proyectos?error={str(e)}",
            status_code=303
        )


@router.get("/proyectos/nuevo")
async def nuevo_proyecto_form(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        user = await get_current_user(request, db)
        if not user or user.rol_id != 2:
            return RedirectResponse(
                url="/proyectos?error=Solo los profesores pueden crear proyectos",
                status_code=303
            )

        estados = db.query(Estado).all()
        materias = db.query(Materia).filter(Materia.estado_id == 1).all()
        alumnos = db.query(Alumno).join(Alumno.persona).filter(
            Alumno.persona.has(estado_id=1)
        ).all()

        # Obtener el profesor actual
        profesor = db.query(Profesor).filter(
            Profesor.persona_id == user.persona_id
        ).first()

        if not profesor:
            return RedirectResponse(
                url="/proyectos?error=No se encontró el registro de profesor",
                status_code=303
            )

        return templates.TemplateResponse(
            "proyectos/crear.html",
            {
                "request": request,
                "estados": estados,
                "materias": materias,
                "alumnos": alumnos,
                "profesor": profesor,
                "user": user
            }
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/proyectos?error={str(e)}",
            status_code=303
        )


@router.post("/proyectos")
async def crear_proyecto(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        user = await get_current_user(request, db)
        if not user or user.rol_id != 2:
            return RedirectResponse(
                url="/proyectos?error=Solo los profesores pueden crear proyectos",
                status_code=303
            )

        profesor = db.query(Profesor).filter(
            Profesor.persona_id == user.persona_id
        ).first()

        if not profesor:
            return RedirectResponse(
                url="/proyectos?error=No se encontró el registro de profesor",
                status_code=303
            )

        form = await request.form()

        nuevo_proyecto = Proyecto(
            nombre=form.get("nombre"),
            descripcion=form.get("descripcion"),
            estado_id=int(form.get("estado_id")),
            profesor_id=profesor.id,
            fecha=datetime.now()
        )
        db.add(nuevo_proyecto)
        db.flush()

        # Asignar materias
        materia_ids = form.getlist("materia_ids")
        for materia_id in materia_ids:
            proyecto_materia = ProyectoXMateria(
                proyecto_id=nuevo_proyecto.id,
                materias_id=int(materia_id),
                profesores_id=profesor.id
            )
            db.add(proyecto_materia)

        # Asignar alumnos
        alumno_ids = form.getlist("alumno_ids")
        for alumno_id in alumno_ids:
            alumno_proyecto = AlumnosXProyecto(
                proyecto_id=nuevo_proyecto.id,
                alumnos_id=int(alumno_id)
            )
            db.add(alumno_proyecto)

        db.commit()
        return RedirectResponse(
            url="/proyectos?exito=Proyecto creado exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/proyectos/nuevo?error={str(e)}",
            status_code=303
        )


@router.get("/proyectos/{proyecto_id}")
async def ver_proyecto(
        request: Request,
        proyecto_id: int,
        db: Session = Depends(get_db)
):
    try:
        user = await get_current_user(request, db)
        proyecto = db.query(Proyecto).options(
            joinedload(Proyecto.estado),
            joinedload(Proyecto.profesor).joinedload(Profesor.persona),
            joinedload(Proyecto.materias).joinedload(ProyectoXMateria.materia),
            joinedload(Proyecto.alumnos).joinedload(AlumnosXProyecto.alumno).joinedload(Alumno.persona),
            joinedload(Proyecto.archivos).joinedload(ArchivosXProyecto.tipo_archivo)  # Agregar esta línea
        ).filter(Proyecto.id == proyecto_id).first()

        if not proyecto:
            return RedirectResponse(
                url="/proyectos?error=Proyecto no encontrado",
                status_code=303
            )

        # Obtener permisos del usuario
        permissions = await get_user_permissions(user, proyecto_id, db) if user else {}

        # Obtener tipos de archivos para el modal
        tipos_archivos = db.query(TiposArchivos).all()

        return templates.TemplateResponse(
            "proyectos/detalle.html",
            {
                "request": request,
                "proyecto": proyecto,
                "user": user,
                "can_edit": permissions.get("can_edit", False),
                "can_delete": permissions.get("can_delete", False),
                "is_vinculado": permissions.get("is_vinculado", False),
                "tipos_archivos": tipos_archivos  # Agregar esta línea
            }
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/proyectos?error={str(e)}",
            status_code=303
        )


@router.get("/proyectos/{proyecto_id}/editar")
async def editar_proyecto_form(
        request: Request,
        proyecto_id: int,
        db: Session = Depends(get_db)
):
    try:
        user = await get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=303)

        permissions = await get_user_permissions(user, proyecto_id, db)
        if not permissions["can_edit"]:
            return RedirectResponse(
                url=f"/proyectos/{proyecto_id}?error=No tienes permisos para editar este proyecto",
                status_code=303
            )

        proyecto = db.query(Proyecto).options(
            joinedload(Proyecto.materias),
            joinedload(Proyecto.alumnos)
        ).filter(Proyecto.id == proyecto_id).first()

        if not proyecto:
            return RedirectResponse(
                url="/proyectos?error=Proyecto no encontrado",
                status_code=303
            )

        estados = db.query(Estado).all()
        materias = db.query(Materia).filter(Materia.estado_id == 1).all()
        alumnos = db.query(Alumno).join(Alumno.persona).filter(
            Alumno.persona.has(estado_id=1)
        ).all()

        return templates.TemplateResponse(
            "proyectos/editar.html",
            {
                "request": request,
                "proyecto": proyecto,
                "estados": estados,
                "materias": materias,
                "alumnos": alumnos,
                "user": user,
                "is_profesor": user.rol_id == 2,
                "can_edit": permissions["can_edit"],
                "can_delete": permissions["can_delete"]
            }
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/proyectos?error={str(e)}",
            status_code=303
        )


@router.post("/proyectos/{proyecto_id}/editar")
async def editar_proyecto(
        request: Request,
        proyecto_id: int,
        db: Session = Depends(get_db)
):
    try:
        user = await get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=303)

        permissions = await get_user_permissions(user, proyecto_id, db)
        if not permissions["can_edit"]:
            return RedirectResponse(
                url=f"/proyectos/{proyecto_id}?error=No tienes permisos para editar este proyecto",
                status_code=303
            )

        form = await request.form()
        proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()

        if not proyecto:
            return RedirectResponse(
                url="/proyectos?error=Proyecto no encontrado",
                status_code=303
            )

        # Actualizar datos básicos (permitido para profesores y alumnos vinculados)
        proyecto.nombre = form.get("nombre")
        proyecto.descripcion = form.get("descripcion")
        proyecto.estado_id = int(form.get("estado_id"))

        # Solo los profesores pueden actualizar materias y alumnos
        if user.rol_id == 2:
            # Verificar que sea el profesor del proyecto
            profesor = db.query(Profesor).filter(
                Profesor.persona_id == user.persona_id
            ).first()

            if profesor and profesor.id == proyecto.profesor_id:
                # Actualizar materias
                db.query(ProyectoXMateria).filter(
                    ProyectoXMateria.proyecto_id == proyecto_id
                ).delete()

                materia_ids = form.getlist("materia_ids")
                for materia_id in materia_ids:
                    proyecto_materia = ProyectoXMateria(
                        proyecto_id=proyecto_id,
                        materias_id=int(materia_id),
                        profesores_id=profesor.id
                    )
                    db.add(proyecto_materia)

                # Actualizar alumnos
                db.query(AlumnosXProyecto).filter(
                    AlumnosXProyecto.proyecto_id == proyecto_id
                ).delete()

                alumno_ids = form.getlist("alumno_ids")
                for alumno_id in alumno_ids:
                    alumno_proyecto = AlumnosXProyecto(
                        proyecto_id=proyecto_id,
                        alumnos_id=int(alumno_id)
                    )
                    db.add(alumno_proyecto)

        db.commit()
        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}?exito=Proyecto actualizado exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/proyectos/{proyecto_id}/editar?error={str(e)}",
            status_code=303
        )


@router.post("/proyectos/{proyecto_id}/eliminar")
async def eliminar_proyecto(
        request: Request,
        proyecto_id: int,
        db: Session = Depends(get_db)
):
    try:
        user = await get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=303)

        permissions = await get_user_permissions(user, proyecto_id, db)
        if not permissions["can_delete"]:
            return RedirectResponse(
                url=f"/proyectos/{proyecto_id}?error=Solo el profesor puede eliminar el proyecto",
                status_code=303
            )

        proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
        if not proyecto:
            return RedirectResponse(
                url="/proyectos?error=Proyecto no encontrado",
                status_code=303
            )

        # Eliminar relaciones
        db.query(ProyectoXMateria).filter(
            ProyectoXMateria.proyecto_id == proyecto_id
        ).delete()
        db.query(AlumnosXProyecto).filter(
            AlumnosXProyecto.proyecto_id == proyecto_id
        ).delete()

        db.delete(proyecto)
        db.commit()

        return RedirectResponse(
            url="/proyectos?exito=Proyecto eliminado exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/proyectos?error={str(e)}",
            status_code=303
        )