from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Persona, Rol, Estado, Alumno, Profesor, Carrera
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/personas")
async def listar_personas(request: Request, db: Session = Depends(get_db)):
    personas = db.query(Persona).all()
    roles = db.query(Rol).all()
    estados = db.query(Estado).all()
    carreras = db.query(Carrera).all()  # Para el select de carreras si es alumno
    return templates.TemplateResponse(
        "personas/index.html",
        {
            "request": request,
            "personas": personas,
            "roles": roles,
            "estados": estados,
            "carreras": carreras
        }
    )


@router.post("/personas")
async def crear_persona(
        nombres: str = Form(...),
        apellidos: str = Form(...),
        rol_id: int = Form(...),
        estado_id: int = Form(...),
        telefono: str = Form(...),
        correo: str = Form(...),
        matricula: str = Form(...),
        carreras_id: Optional[int] = Form(None),  # Opcional, solo para alumnos
        db: Session = Depends(get_db)
):
    try:
        # Crear la persona
        nueva_persona = Persona(
            nombres=nombres,
            apellidos=apellidos,
            rol_id=rol_id,
            estado_id=estado_id,
            telefono=telefono,
            correo=correo
        )
        db.add(nueva_persona)
        db.flush()  # Para obtener el ID de la persona

        # Según el rol, crear el registro correspondiente
        if rol_id == 2:  # Profesor
            nuevo_profesor = Profesor(
                persona_id=nueva_persona.id,
                matricula=matricula
            )
            db.add(nuevo_profesor)
        elif rol_id == 3:  # Alumno
            if not carreras_id:
                raise HTTPException(status_code=400, detail="Se requiere una carrera para los alumnos")
            nuevo_alumno = Alumno(
                persona_id=nueva_persona.id,
                matricula=matricula,
                carreras_id=carreras_id
            )
            db.add(nuevo_alumno)

        db.commit()
        return RedirectResponse(url="/personas", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/personas/{persona_id}")
async def obtener_persona(request: Request, persona_id: int, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    roles = db.query(Rol).all()
    estados = db.query(Estado).all()
    carreras = db.query(Carrera).all()

    # Obtener matrícula según el rol
    matricula = None
    carrera_id = None
    if persona.rol_id == 2:  # Profesor
        profesor = db.query(Profesor).filter(Profesor.persona_id == persona_id).first()
        if profesor:
            matricula = profesor.matricula
    elif persona.rol_id == 3:  # Alumno
        alumno = db.query(Alumno).filter(Alumno.persona_id == persona_id).first()
        if alumno:
            matricula = alumno.matricula
            carrera_id = alumno.carreras_id

    return templates.TemplateResponse(
        "personas/editar.html",
        {
            "request": request,
            "persona": persona,
            "roles": roles,
            "estados": estados,
            "carreras": carreras,
            "matricula": matricula,
            "carrera_id": carrera_id
        }
    )


@router.post("/personas/{persona_id}/editar")
async def editar_persona(
        persona_id: int,
        nombres: str = Form(...),
        apellidos: str = Form(...),
        rol_id: int = Form(...),
        estado_id: int = Form(...),
        telefono: str = Form(...),
        correo: str = Form(...),
        matricula: str = Form(...),
        carreras_id: Optional[int] = Form(None),
        db: Session = Depends(get_db)
):
    try:
        persona = db.query(Persona).filter(Persona.id == persona_id).first()
        if not persona:
            return RedirectResponse(
                url="/personas?error=Persona no encontrada",
                status_code=303
            )

        # Actualizar datos básicos de la persona
        persona.nombres = nombres
        persona.apellidos = apellidos
        persona.rol_id = rol_id
        persona.estado_id = estado_id
        persona.telefono = telefono
        persona.correo = correo

        # Manejar el cambio de rol
        # Si era profesor, eliminar registro de profesor
        if persona.profesor:
            db.delete(persona.profesor[0])

        # Si era alumno, eliminar registro de alumno
        if persona.alumno:
            db.delete(persona.alumno[0])

        # Crear nuevo registro según el rol
        if rol_id == 2:  # Profesor
            nuevo_profesor = Profesor(
                persona_id=persona_id,
                matricula=matricula
            )
            db.add(nuevo_profesor)
        elif rol_id == 3:  # Alumno
            if not carreras_id:
                return RedirectResponse(
                    url=f"/personas?error=Se requiere una carrera para los alumnos",
                    status_code=303
                )
            nuevo_alumno = Alumno(
                persona_id=persona_id,
                matricula=matricula,
                carreras_id=carreras_id
            )
            db.add(nuevo_alumno)

        db.commit()
        return RedirectResponse(url="/personas?exito=Persona actualizada exitosamente", status_code=303)
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/personas?error={str(e)}",
            status_code=303
        )


@router.get("/personas/{persona_id}")
async def obtener_persona(request: Request, persona_id: int, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    roles = db.query(Rol).all()
    estados = db.query(Estado).all()
    carreras = db.query(Carrera).all()

    # Obtener matrícula y carrera si existe
    matricula = None
    carrera_id = None
    if persona.rol_id == 2 and persona.profesor:  # Profesor
        matricula = persona.profesor[0].matricula if persona.profesor else None
    elif persona.rol_id == 3 and persona.alumno:  # Alumno
        matricula = persona.alumno[0].matricula if persona.alumno else None
        carrera_id = persona.alumno[0].carreras_id if persona.alumno else None

    return templates.TemplateResponse(
        "personas/editar.html",
        {
            "request": request,
            "persona": persona,
            "roles": roles,
            "estados": estados,
            "carreras": carreras,
            "matricula": matricula,
            "carrera_id": carrera_id
        }
    )


@router.post("/personas/{persona_id}/eliminar")
async def eliminar_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    try:
        # Eliminar registros relacionados
        db.query(Profesor).filter(Profesor.persona_id == persona_id).delete()
        db.query(Alumno).filter(Alumno.persona_id == persona_id).delete()
        db.delete(persona)
        db.commit()
        return RedirectResponse(url="/personas", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))