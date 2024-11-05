from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Profesor, Materia, Persona
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import List

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/profesores/{profesor_id}/materias")
async def ver_materias_profesor(request: Request, profesor_id: int, db: Session = Depends(get_db)):
    profesor = db.query(Profesor).options(
        joinedload(Profesor.persona),
        joinedload(Profesor.materias)
    ).filter(Profesor.id == profesor_id).first()

    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    # Obtener todas las materias disponibles
    materias_disponibles = db.query(Materia).filter(
        ~Materia.id.in_([m.id for m in profesor.materias])
    ).all()

    return templates.TemplateResponse(
        "profesor_materias/asignacion.html",
        {
            "request": request,
            "profesor": profesor,
            "materias_disponibles": materias_disponibles,
            "mensaje_error": request.query_params.get("error"),
            "mensaje_exito": request.query_params.get("exito")
        }
    )

@router.post("/profesores/{profesor_id}/asignar-materia")
async def asignar_materia(
    profesor_id: int,
    materia_id: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        profesor = db.query(Profesor).filter(Profesor.id == profesor_id).first()
        if not profesor:
            return RedirectResponse(
                url=f"/profesores/{profesor_id}/materias?error=Profesor no encontrado",
                status_code=303
            )

        materia = db.query(Materia).filter(Materia.id == materia_id).first()
        if not materia:
            return RedirectResponse(
                url=f"/profesores/{profesor_id}/materias?error=Materia no encontrada",
                status_code=303
            )

        profesor.materias.append(materia)
        db.commit()
        return RedirectResponse(
            url=f"/profesores/{profesor_id}/materias?exito=Materia asignada exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/profesores/{profesor_id}/materias?error={str(e)}",
            status_code=303
        )

@router.post("/profesores/{profesor_id}/quitar-materia/{materia_id}")
async def quitar_materia(
    profesor_id: int,
    materia_id: int,
    db: Session = Depends(get_db)
):
    try:
        profesor = db.query(Profesor).filter(Profesor.id == profesor_id).first()
        if not profesor:
            return RedirectResponse(
                url=f"/profesores/{profesor_id}/materias?error=Profesor no encontrado",
                status_code=303
            )

        materia = db.query(Materia).filter(Materia.id == materia_id).first()
        if not materia:
            return RedirectResponse(
                url=f"/profesores/{profesor_id}/materias?error=Materia no encontrada",
                status_code=303
            )

        profesor.materias.remove(materia)
        db.commit()
        return RedirectResponse(
            url=f"/profesores/{profesor_id}/materias?exito=Materia removida exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/profesores/{profesor_id}/materias?error={str(e)}",
            status_code=303
        )