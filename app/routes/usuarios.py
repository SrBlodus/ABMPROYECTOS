from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Usuario, Persona, Rol, Estado
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from .auth import get_current_user
import bcrypt
from typing import Optional

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

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

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

@router.get("")
async def listar_usuarios(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        usuarios = db.query(Usuario).options(
            joinedload(Usuario.persona),
            joinedload(Usuario.rol),
            joinedload(Usuario.estado)
        ).all()

        return templates.TemplateResponse(
            "usuarios/index.html",
            {
                "request": request,
                "usuarios": usuarios,
                "user": current_user
            }
        )
    except Exception as e:
        return RedirectResponse(
            url="/usuarios?error=" + str(e),
            status_code=303
        )

@router.get("/nuevo")
async def nuevo_usuario_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        personas_sin_usuario = db.query(Persona).outerjoin(Usuario).filter(Usuario.id == None).all()
        roles = db.query(Rol).all()
        estados = db.query(Estado).all()

        return templates.TemplateResponse(
            "usuarios/crear.html",
            {
                "request": request,
                "personas": personas_sin_usuario,
                "roles": roles,
                "estados": estados,
                "user": current_user
            }
        )
    except Exception as e:
        return RedirectResponse(
            url="/usuarios?error=" + str(e),
            status_code=303
        )

@router.post("")
async def crear_usuario(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        form = await request.form()

        # Validaciones
        if db.query(Usuario).filter(Usuario.persona_id == form.get("persona_id")).first():
            raise HTTPException(status_code=400, detail="Esta persona ya tiene un usuario asignado")

        if db.query(Usuario).filter(Usuario.usuario == form.get("usuario")).first():
            raise HTTPException(status_code=400, detail="Este nombre de usuario ya existe")

        nuevo_usuario = Usuario(
            usuario=form.get("usuario"),
            password=get_password_hash(form.get("password")),
            rol_id=int(form.get("rol_id")),
            persona_id=int(form.get("persona_id")),
            estado_id=int(form.get("estado_id"))
        )

        db.add(nuevo_usuario)
        db.commit()

        return RedirectResponse(
            url="/usuarios?exito=Usuario creado exitosamente",
            status_code=303
        )
    except HTTPException as he:
        return RedirectResponse(
            url="/usuarios/nuevo?error=" + str(he.detail),
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url="/usuarios/nuevo?error=" + str(e),
            status_code=303
        )

@router.get("/{usuario_id}")
async def ver_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        usuario = db.query(Usuario).options(
            joinedload(Usuario.persona),
            joinedload(Usuario.rol),
            joinedload(Usuario.estado)
        ).filter(Usuario.id == usuario_id).first()

        if not usuario:
            return RedirectResponse(
                url="/usuarios?error=Usuario no encontrado",
                status_code=303
            )

        return templates.TemplateResponse(
            "usuarios/detalle.html",
            {
                "request": request,
                "usuario": usuario,
                "user": current_user
            }
        )
    except Exception as e:
        return RedirectResponse(
            url="/usuarios?error=" + str(e),
            status_code=303
        )

@router.get("/{usuario_id}/editar")
async def editar_usuario_form(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        usuario = db.query(Usuario).options(
            joinedload(Usuario.persona),
            joinedload(Usuario.rol),
            joinedload(Usuario.estado)
        ).filter(Usuario.id == usuario_id).first()

        if not usuario:
            return RedirectResponse(
                url="/usuarios?error=Usuario no encontrado",
                status_code=303
            )

        roles = db.query(Rol).all()
        estados = db.query(Estado).all()

        return templates.TemplateResponse(
            "usuarios/editar.html",
            {
                "request": request,
                "usuario": usuario,
                "roles": roles,
                "estados": estados,
                "user": current_user
            }
        )
    except Exception as e:
        return RedirectResponse(
            url="/usuarios?error=" + str(e),
            status_code=303
        )

@router.post("/{usuario_id}/editar")
async def editar_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        form = await request.form()
        db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

        if not db_usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # No permitir la edición del propio usuario admin
        if current_user.id == usuario_id:
            raise HTTPException(status_code=400, detail="No puedes modificar tu propio usuario administrador")

        if (form.get("usuario") != db_usuario.usuario and
                db.query(Usuario).filter(Usuario.usuario == form.get("usuario")).first()):
            raise HTTPException(status_code=400, detail="Este nombre de usuario ya existe")

        db_usuario.usuario = form.get("usuario")
        if form.get("password"):
            db_usuario.password = get_password_hash(form.get("password"))
        db_usuario.rol_id = int(form.get("rol_id"))
        db_usuario.estado_id = int(form.get("estado_id"))

        db.commit()

        return RedirectResponse(
            url=f"/usuarios/{usuario_id}?exito=Usuario actualizado exitosamente",
            status_code=303
        )
    except HTTPException as he:
        return RedirectResponse(
            url=f"/usuarios/{usuario_id}/editar?error={str(he.detail)}",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/usuarios/{usuario_id}/editar?error={str(e)}",
            status_code=303
        )

@router.post("/{usuario_id}/eliminar")
async def eliminar_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verify_admin)
):
    try:
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            return RedirectResponse(
                url="/usuarios?error=Usuario no encontrado",
                status_code=303
            )

        # No permitir la desactivación del propio usuario admin
        if current_user.id == usuario_id:
            return RedirectResponse(
                url="/usuarios?error=No puedes desactivar tu propio usuario administrador",
                status_code=303
            )

        # En lugar de eliminar, actualizamos el estado a inactivo
        usuario.estado_id = 2
        db.commit()

        return RedirectResponse(
            url="/usuarios?exito=Usuario desactivado exitosamente",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/usuarios?error={str(e)}",
            status_code=303
        )