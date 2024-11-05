from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Facultad, Carrera, Materia, Estado
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# Rutas para Facultades
@router.get("/facultades")
async def listar_facultades(request: Request, db: Session = Depends(get_db)):
    facultades = db.query(Facultad).options(joinedload(Facultad.carreras)).all()
    estados = db.query(Estado).all()
    return templates.TemplateResponse(
        "academic/facultades.html",
        {
            "request": request,
            "facultades": facultades,
            "estados": estados,
            "mensaje_error": request.query_params.get("error"),
            "mensaje_exito": request.query_params.get("exito")
        }
    )


@router.post("/facultades")
async def crear_facultad(
        codigo: str = Form(...),
        nombre: str = Form(...),
        estado_id: int = Form(...),
        db: Session = Depends(get_db)
):
    try:
        # Verificar si el código ya existe
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


@router.post("/facultades/{facultad_id}/editar")
async def editar_facultad(
        facultad_id: int,
        codigo: str = Form(...),
        nombre: str = Form(...),
        estado_id: int = Form(...),
        db: Session = Depends(get_db)
):
    try:
        facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
        if not facultad:
            raise HTTPException(status_code=404, detail="Facultad no encontrada")

        # Verificar si el código ya existe (excluyendo la facultad actual)
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


# Rutas para Carreras
@router.get("/facultades/{facultad_id}/carreras")
async def listar_carreras(request: Request, facultad_id: int, db: Session = Depends(get_db)):
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
            "mensaje_exito": request.query_params.get("exito")
        }
    )


@router.post("/facultades/{facultad_id}/carreras")
async def crear_carrera(
        facultad_id: int,
        codigo: str = Form(...),
        nombre: str = Form(...),
        estado_id: int = Form(...),
        db: Session = Depends(get_db)
):
    try:
        # Verificar si el código ya existe
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


@router.post("/carreras/{carrera_id}/editar")
async def editar_carrera(
        carrera_id: int,
        codigo: str = Form(...),
        nombre: str = Form(...),
        estado_id: int = Form(...),
        db: Session = Depends(get_db)
):
    try:
        carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
        if not carrera:
            raise HTTPException(status_code=404, detail="Carrera no encontrada")

        # Verificar si el código ya existe (excluyendo la carrera actual)
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
async def eliminar_carrera(carrera_id: int, db: Session = Depends(get_db)):
    carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")

    facultad_id = carrera.facultades_id
    try:
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


# Rutas para Materias
@router.get("/carreras/{carrera_id}/materias")
async def listar_materias(request: Request, carrera_id: int, db: Session = Depends(get_db)):
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
            "mensaje_exito": request.query_params.get("exito")
        }
    )


@router.post("/carreras/{carrera_id}/materias")
async def crear_materia(
        carrera_id: int,
        codigo: str = Form(...),
        nombre: str = Form(...),
        curso: int = Form(...),
        estado_id: int = Form(...),
        db: Session = Depends(get_db)
):
    try:
        # Verificar si el código ya existe
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


@router.post("/materias/{materia_id}/editar")
async def editar_materia(
        materia_id: int,
        codigo: str = Form(...),
        nombre: str = Form(...),
        curso: int = Form(...),
        estado_id: int = Form(...),
        db: Session = Depends(get_db)
):
    try:
        materia = db.query(Materia).filter(Materia.id == materia_id).first()
        if not materia:
            raise HTTPException(status_code=404, detail="Materia no encontrada")

        # Verificar si el código ya existe (excluyendo la materia actual)
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
async def eliminar_materia(materia_id: int, db: Session = Depends(get_db)):
    materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if not materia:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    carrera_id = materia.carreras_id
    try:
        # Aquí podrías agregar verificaciones adicionales si es necesario
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


@router.post("/facultades/{facultad_id}/eliminar")
async def eliminar_facultad(facultad_id: int, db: Session = Depends(get_db)):
    try:
        facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
        if not facultad:
            return RedirectResponse(
                url="/facultades?error=Facultad no encontrada",
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
