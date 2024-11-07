from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Facultad, Carrera, Materia, Estado, Usuario
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from .auth import get_current_user
from typing import Optional
from sqlalchemy import text

from ..models.models import profesor_materia, ProyectoXMateria

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

# Función para establecer el usuario de auditoría
def set_audit_user(db: Session, user_id: int):
    try:
        db.execute(text("SET @user_id = :user_id"), {"user_id": user_id})
    except Exception as e:
        print(f"Error al establecer usuario de auditoría: {str(e)}")

# Rutas para Facultades
@router.get("/facultades")
async def listar_facultades(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    facultades = db.query(Facultad).options(joinedload(Facultad.carreras)).all()
    estados = db.query(Estado).all()
    return templates.TemplateResponse(
        "academic/facultades.html",
        {
            "request": request,
            "facultades": facultades,
            "estados": estados,
            "mensaje_error": request.query_params.get("error"),
            "mensaje_exito": request.query_params.get("exito"),
            "user": current_user
        }
    )

@router.post("/facultades")
async def crear_facultad(
    request: Request,
    codigo: str = Form(...),
    nombre: str = Form(...),
    estado_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        facultad_existente = db.query(Facultad).filter(Facultad.codigo == codigo.upper()).first()
        if facultad_existente:
            return RedirectResponse(
                url=f"/facultades?error=El código {codigo} ya está en uso",
                status_code=303
            )

        nueva_facultad = Facultad(
            codigo=codigo.upper(),
            nombre=nombre,
            estado_id=estado_id
        )
        db.add(nueva_facultad)
        db.commit()
        return RedirectResponse(
            url="/facultades?exito=Facultad creada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/facultades?error={str(e)}",
            status_code=303
        )

@router.get("/facultades/{facultad_id}/carreras")
async def listar_carreras(
    request: Request,
    facultad_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
    if not facultad:
        raise HTTPException(status_code=404, detail="Facultad no encontrada")

    carreras = db.query(Carrera).filter(Carrera.facultades_id == facultad_id).all()
    estados = db.query(Estado).all()
    return templates.TemplateResponse(
        "academic/carreras.html",
        {
            "request": request,
            "facultad": facultad,
            "carreras": carreras,
            "estados": estados,
            "mensaje_error": request.query_params.get("error"),
            "mensaje_exito": request.query_params.get("exito"),
            "user": current_user
        }
    )

@router.post("/facultades/{facultad_id}/carreras")
async def crear_carrera(
    request: Request,
    facultad_id: int,
    codigo: str = Form(...),
    nombre: str = Form(...),
    estado_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        carrera_existente = db.query(Carrera).filter(Carrera.codigo == codigo.upper()).first()
        if carrera_existente:
            return RedirectResponse(
                url=f"/facultades/{facultad_id}/carreras?error=El código {codigo} ya está en uso",
                status_code=303
            )

        nueva_carrera = Carrera(
            codigo=codigo.upper(),
            nombre=nombre,
            facultades_id=facultad_id,
            estado_id=estado_id
        )
        db.add(nueva_carrera)
        db.commit()
        return RedirectResponse(
            url=f"/facultades/{facultad_id}/carreras?exito=Carrera creada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/facultades/{facultad_id}/carreras?error={str(e)}",
            status_code=303
        )

@router.get("/carreras/{carrera_id}/materias")
async def listar_materias(
    request: Request,
    carrera_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")

    materias = db.query(Materia).filter(Materia.carreras_id == carrera_id).all()
    estados = db.query(Estado).all()
    return templates.TemplateResponse(
        "academic/materias.html",
        {
            "request": request,
            "carrera": carrera,
            "materias": materias,
            "estados": estados,
            "mensaje_error": request.query_params.get("error"),
            "mensaje_exito": request.query_params.get("exito"),
            "user": current_user
        }
    )

@router.post("/carreras/{carrera_id}/materias")
async def crear_materia(
    request: Request,
    carrera_id: int,
    codigo: str = Form(...),
    nombre: str = Form(...),
    curso: int = Form(...),
    estado_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        materia_existente = db.query(Materia).filter(Materia.codigo == codigo.upper()).first()
        if materia_existente:
            return RedirectResponse(
                url=f"/carreras/{carrera_id}/materias?error=El código {codigo} ya está en uso",
                status_code=303
            )

        nueva_materia = Materia(
            codigo=codigo.upper(),
            nombre=nombre,
            carreras_id=carrera_id,
            curso=curso,
            estado_id=estado_id
        )
        db.add(nueva_materia)
        db.commit()
        return RedirectResponse(
            url=f"/carreras/{carrera_id}/materias?exito=Materia creada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/carreras/{carrera_id}/materias?error={str(e)}",
            status_code=303
        )

@router.post("/facultades/{facultad_id}/editar")
async def editar_facultad(
        request: Request,
        facultad_id: int,
        codigo: str = Form(...),
        nombre: str = Form(...),
        estado_id: int = Form(...),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        # Establecer usuario para auditoría
        set_audit_user(db, current_user.id)

        facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
        if not facultad:
            raise HTTPException(status_code=404, detail="Facultad no encontrada")

        facultad_existente = db.query(Facultad).filter(
            Facultad.codigo == codigo.upper(),
            Facultad.id != facultad_id
        ).first()
        if facultad_existente:
            return RedirectResponse(
                url=f"/facultades?error=El código {codigo} ya está en uso",
                status_code=303
            )

        facultad.codigo = codigo.upper()
        facultad.nombre = nombre
        facultad.estado_id = estado_id
        db.commit()

        return RedirectResponse(
            url="/facultades?exito=Facultad actualizada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/facultades?error={str(e)}",
            status_code=303
        )


@router.post("/facultades/{facultad_id}/eliminar")
async def eliminar_facultad(
        request: Request,
        facultad_id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        # Establecer usuario para auditoría
        set_audit_user(db, current_user.id)

        facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
        if not facultad:
            return RedirectResponse(
                url="/facultades?error=Facultad no encontrada",
                status_code=303
            )

        # Verificar si hay carreras asociadas
        carreras = db.query(Carrera).filter(Carrera.facultades_id == facultad_id).first()
        if carreras:
            return RedirectResponse(
                url="/facultades?error=No se puede eliminar la facultad porque tiene carreras asociadas",
                status_code=303
            )

        db.delete(facultad)
        db.commit()

        return RedirectResponse(
            url="/facultades?exito=Facultad eliminada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/facultades?error={str(e)}",
            status_code=303
        )


@router.post("/carreras/{carrera_id}/editar")
async def editar_carrera(
        request: Request,
        carrera_id: int,
        codigo: str = Form(...),
        nombre: str = Form(...),
        estado_id: int = Form(...),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        # Establecer usuario para auditoría
        set_audit_user(db, current_user.id)

        carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
        if not carrera:
            raise HTTPException(status_code=404, detail="Carrera no encontrada")

        carrera_existente = db.query(Carrera).filter(
            Carrera.codigo == codigo.upper(),
            Carrera.id != carrera_id
        ).first()
        if carrera_existente:
            return RedirectResponse(
                url=f"/facultades/{carrera.facultades_id}/carreras?error=El código {codigo} ya está en uso",
                status_code=303
            )

        carrera.codigo = codigo.upper()
        carrera.nombre = nombre
        carrera.estado_id = estado_id
        db.commit()

        return RedirectResponse(
            url=f"/facultades/{carrera.facultades_id}/carreras?exito=Carrera actualizada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/facultades/{carrera.facultades_id}/carreras?error={str(e)}",
            status_code=303
        )


@router.post("/carreras/{carrera_id}/eliminar")
async def eliminar_carrera(
        request: Request,
        carrera_id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        # Establecer usuario para auditoría
        set_audit_user(db, current_user.id)

        carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
        if not carrera:
            raise HTTPException(status_code=404, detail="Carrera no encontrada")

        facultad_id = carrera.facultades_id

        # Verificar si hay materias asociadas
        materias = db.query(Materia).filter(Materia.carreras_id == carrera_id).first()
        if materias:
            return RedirectResponse(
                url=f"/facultades/{facultad_id}/carreras?error=No se puede eliminar la carrera porque tiene materias asociadas",
                status_code=303
            )

        db.delete(carrera)
        db.commit()

        return RedirectResponse(
            url=f"/facultades/{facultad_id}/carreras?exito=Carrera eliminada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/facultades/{facultad_id}/carreras?error={str(e)}",
            status_code=303
        )


@router.post("/materias/{materia_id}/editar")
async def editar_materia(
        request: Request,
        materia_id: int,
        codigo: str = Form(...),
        nombre: str = Form(...),
        curso: int = Form(...),
        estado_id: int = Form(...),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        # Establecer usuario para auditoría
        set_audit_user(db, current_user.id)

        materia = db.query(Materia).filter(Materia.id == materia_id).first()
        if not materia:
            raise HTTPException(status_code=404, detail="Materia no encontrada")

        materia_existente = db.query(Materia).filter(
            Materia.codigo == codigo.upper(),
            Materia.id != materia_id
        ).first()
        if materia_existente:
            return RedirectResponse(
                url=f"/carreras/{materia.carreras_id}/materias?error=El código {codigo} ya está en uso",
                status_code=303
            )

        materia.codigo = codigo.upper()
        materia.nombre = nombre
        materia.curso = curso
        materia.estado_id = estado_id
        db.commit()

        return RedirectResponse(
            url=f"/carreras/{materia.carreras_id}/materias?exito=Materia actualizada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/carreras/{materia.carreras_id}/materias?error={str(e)}",
            status_code=303
        )


@router.post("/materias/{materia_id}/eliminar")
async def eliminar_materia(
        request: Request,
        materia_id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(verify_admin)
):
    try:
        # Establecer usuario para auditoría
        set_audit_user(db, current_user.id)

        materia = db.query(Materia).filter(Materia.id == materia_id).first()
        if not materia:
            raise HTTPException(status_code=404, detail="Materia no encontrada")

        carrera_id = materia.carreras_id

        # Verificar si hay proyectos asociados
        proyectos = db.query(ProyectoXMateria).filter(
            ProyectoXMateria.materias_id == materia_id
        ).first()

        if proyectos:
            return RedirectResponse(
                url=f"/carreras/{carrera_id}/materias?error=No se puede eliminar la materia porque tiene proyectos asociados",
                status_code=303
            )

        # Verificar si hay profesores asignados
        profesores = db.query(profesor_materia).filter(
            profesor_materia.c.materia_id == materia_id
        ).first()

        if profesores:
            return RedirectResponse(
                url=f"/carreras/{carrera_id}/materias?error=No se puede eliminar la materia porque tiene profesores asignados",
                status_code=303
            )

        db.delete(materia)
        db.commit()

        return RedirectResponse(
            url=f"/carreras/{carrera_id}/materias?exito=Materia eliminada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/carreras/{carrera_id}/materias?error={str(e)}",
            status_code=303
        )
