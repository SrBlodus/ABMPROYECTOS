from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Persona, Rol, Estado, Alumno, Profesor, Carrera, Usuario
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Optional
from .auth import get_current_user

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


@router.get("/personas")
async def listar_personas(
        request: Request,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    personas = db.query(Persona).all()
    roles = db.query(Rol).all()
    estados = db.query(Estado).all()
    carreras = db.query(Carrera).all()
    return templates.TemplateResponse(
        "personas/index.html",
        {
            "request": request,
            "personas": personas,
            "roles": roles,
            "estados": estados,
            "carreras": carreras,
            "user": current_user
        }
    )


@router.post("/personas")
async def crear_persona(
        request: Request,
        nombres: str = Form(...),
        apellidos: str = Form(...),
        rol_id: int = Form(...),
        estado_id: int = Form(...),
        telefono: str = Form(...),
        correo: str = Form(...),
        matricula: str = Form(...),
        carreras_id: Optional[int] = Form(None),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
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
        db.flush()

        if rol_id == 2:  # Profesor
            nuevo_profesor = Profesor(
                persona_id=nueva_persona.id,
                matricula=matricula
            )
            db.add(nuevo_profesor)
        elif rol_id == 3:  # Alumno
            if not carreras_id:
                return RedirectResponse(
                    url="/personas?error=Se requiere una carrera para los alumnos",
                    status_code=303
                )
            nuevo_alumno = Alumno(
                persona_id=nueva_persona.id,
                matricula=matricula,
                carreras_id=carreras_id
            )
            db.add(nuevo_alumno)

        db.commit()
        return RedirectResponse(
            url="/personas?exito=Persona creada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/personas?error={str(e)}",
            status_code=303
        )


@router.get("/personas/{persona_id}")
async def obtener_persona(
        request: Request,
        persona_id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        return RedirectResponse(
            url="/personas?error=Persona no encontrada",
            status_code=303
        )

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
            "carrera_id": carrera_id,
            "user": current_user
        }
    )


@router.post("/personas/{persona_id}/editar")
async def editar_persona(
        request: Request,
        persona_id: int,
        nombres: str = Form(...),
        apellidos: str = Form(...),
        rol_id: int = Form(...),
        estado_id: int = Form(...),
        telefono: str = Form(...),
        correo: str = Form(...),
        matricula: str = Form(...),
        carreras_id: Optional[int] = Form(None),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        persona = db.query(Persona).filter(Persona.id == persona_id).first()
        if not persona:
            return RedirectResponse(
                url="/personas?error=Persona no encontrada",
                status_code=303
            )

        # Actualizar datos básicos
        persona.nombres = nombres
        persona.apellidos = apellidos
        persona.rol_id = rol_id
        persona.estado_id = estado_id
        persona.telefono = telefono
        persona.correo = correo

        # Manejar cambios de rol
        if persona.profesor:
            db.delete(persona.profesor[0])
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
        return RedirectResponse(
            url="/personas?exito=Persona actualizada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/personas?error={str(e)}",
            status_code=303
        )


@router.post("/personas/{persona_id}/eliminar")
async def eliminar_persona(
        request: Request,
        persona_id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        persona = db.query(Persona).filter(Persona.id == persona_id).first()
        if not persona:
            return RedirectResponse(
                url="/personas?error=Persona no encontrada",
                status_code=303
            )

        # Verificar si la persona tiene un usuario asociado
        if persona.usuario:
            return RedirectResponse(
                url="/personas?error=No se puede eliminar la persona porque tiene un usuario asociado",
                status_code=303
            )

        # Eliminar registros relacionados
        db.query(Profesor).filter(Profesor.persona_id == persona_id).delete()
        db.query(Alumno).filter(Alumno.persona_id == persona_id).delete()
        db.delete(persona)
        db.commit()

        return RedirectResponse(
            url="/personas?exito=Persona eliminada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/personas?error={str(e)}",
            status_code=303
        )