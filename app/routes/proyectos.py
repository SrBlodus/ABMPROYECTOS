from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Proyecto, Estado, ProyectoXMateria, AlumnosXProyecto, Materia, Alumno, Profesor
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import List
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/proyectos")
async def listar_proyectos(request: Request, db: Session = Depends(get_db)):
    proyectos = db.query(Proyecto).all()
    return templates.TemplateResponse(
        "proyectos/index.html",
        {
            "request": request,
            "proyectos": proyectos
        }
    )


@router.get("/proyectos/nuevo")
async def nuevo_proyecto_form(request: Request, db: Session = Depends(get_db)):
    estados = db.query(Estado).all()
    materias = db.query(Materia).filter(Materia.estado_id == 1).all()
    alumnos = db.query(Alumno).join(Alumno.persona).filter(
        Alumno.persona.has(estado_id=1)
    ).all()
    profesores = db.query(Profesor).join(Profesor.persona).filter(
        Profesor.persona.has(estado_id=1)
    ).all()

    return templates.TemplateResponse(
        "proyectos/crear.html",
        {
            "request": request,
            "estados": estados,
            "materias": materias,
            "alumnos": alumnos,
            "profesores": profesores
        }
    )


@router.post("/proyectos")
async def crear_proyecto(
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        # Obtener datos del formulario
        form = await request.form()
        print("Datos del formulario:", dict(form))  # Debug

        nombre = form.get("nombre")
        descripcion = form.get("descripcion")
        estado_id = int(form.get("estado_id"))
        profesor_id = int(form.get("profesor_id"))

        # Los campos múltiples vienen como lista
        materia_ids = form.getlist("materia_ids")
        alumno_ids = form.getlist("alumno_ids")

        print("Materias:", materia_ids)  # Debug
        print("Alumnos:", alumno_ids)  # Debug

        nuevo_proyecto = Proyecto(
            nombre=nombre,
            descripcion=descripcion,
            estado_id=estado_id,
            profesor_id=profesor_id,
            fecha=datetime.now()
        )
        db.add(nuevo_proyecto)
        db.flush()

        # Asignar materias
        for materia_id in materia_ids:
            proyecto_materia = ProyectoXMateria(
                proyecto_id=nuevo_proyecto.id,
                materias_id=int(materia_id),
                profesores_id=profesor_id
            )
            db.add(proyecto_materia)

        # Asignar alumnos
        for alumno_id in alumno_ids:
            alumno_proyecto = AlumnosXProyecto(
                proyecto_id=nuevo_proyecto.id,
                alumnos_id=int(alumno_id)
            )
            db.add(alumno_proyecto)

        db.commit()
        return RedirectResponse(
            url=f"/proyectos?exito=Proyecto creado exitosamente",
            status_code=303
        )
    except Exception as e:
        print("Error al crear proyecto:", str(e))  # Debug
        db.rollback()
        return RedirectResponse(
            url=f"/proyectos/nuevo?error={str(e)}",
            status_code=303
        )


@router.get("/proyectos/{proyecto_id}")
async def ver_proyecto(request: Request, proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).options(
        joinedload(Proyecto.estado),
        joinedload(Proyecto.profesor).joinedload(Profesor.persona),
        joinedload(Proyecto.materias).joinedload(ProyectoXMateria.materia),
        joinedload(Proyecto.alumnos).joinedload(AlumnosXProyecto.alumno).joinedload(Alumno.persona)
    ).filter(Proyecto.id == proyecto_id).first()

    if not proyecto:
        return RedirectResponse(
            url="/proyectos?error=Proyecto no encontrado",
            status_code=303
        )

    return templates.TemplateResponse(
        "proyectos/detalle.html",
        {
            "request": request,
            "proyecto": proyecto
        }
    )


@router.get("/proyectos/{proyecto_id}/editar")
async def editar_proyecto_form(request: Request, proyecto_id: int, db: Session = Depends(get_db)):
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
    profesores = db.query(Profesor).join(Profesor.persona).filter(
        Profesor.persona.has(estado_id=1)
    ).all()

    return templates.TemplateResponse(
        "proyectos/editar.html",
        {
            "request": request,
            "proyecto": proyecto,
            "estados": estados,
            "materias": materias,
            "alumnos": alumnos,
            "profesores": profesores
        }
    )


@router.post("/proyectos/{proyecto_id}/editar")
async def editar_proyecto(
        proyecto_id: int,
        nombre: str = Form(...),
        descripcion: str = Form(...),
        estado_id: int = Form(...),
        profesor_id: int = Form(...),
        materia_ids: List[int] = Form([]),
        alumno_ids: List[int] = Form([]),
        db: Session = Depends(get_db)
):
    try:
        proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
        if not proyecto:
            return RedirectResponse(
                url="/proyectos?error=Proyecto no encontrado",
                status_code=303
            )

        # Actualizar datos básicos
        proyecto.nombre = nombre
        proyecto.descripcion = descripcion
        proyecto.estado_id = estado_id
        proyecto.profesor_id = profesor_id

        # Actualizar materias
        db.query(ProyectoXMateria).filter(
            ProyectoXMateria.proyecto_id == proyecto_id
        ).delete()
        for materia_id in materia_ids:
            proyecto_materia = ProyectoXMateria(
                proyecto_id=proyecto_id,
                materias_id=materia_id,
                profesores_id=profesor_id
            )
            db.add(proyecto_materia)

        # Actualizar alumnos
        db.query(AlumnosXProyecto).filter(
            AlumnosXProyecto.proyecto_id == proyecto_id
        ).delete()
        for alumno_id in alumno_ids:
            alumno_proyecto = AlumnosXProyecto(
                proyecto_id=proyecto_id,
                alumnos_id=alumno_id
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
async def eliminar_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    try:
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

        # Eliminar el proyecto
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