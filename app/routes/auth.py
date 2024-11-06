from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Usuario
from fastapi.templating import Jinja2Templates
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Configuración de JWT
SECRET_KEY = "tu_clave_secreta_muy_segura"  # En producción, usar variable de entorno
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            return None

        user = db.query(Usuario).options(
            joinedload(Usuario.persona),
            joinedload(Usuario.rol)
        ).filter(Usuario.id == user_id).first()
        return user
    except:
        return None


def login_required(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401)
    return user


@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )


@router.post("/login")
async def login(
        request: Request,
        response: Response,
        usuario: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    # Buscar usuario
    user = db.query(Usuario).filter(
        Usuario.usuario == usuario,
        Usuario.estado_id == 1  # Asumiendo que 1 es el estado activo
    ).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Usuario o contraseña incorrectos"
            }
        )

    # Crear token
    access_token = create_access_token(
        data={
            "sub": user.usuario,
            "id": user.id,
            "rol": user.rol_id
        }
    )

    # Crear respuesta de redirección
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=3600,  # 1 hora
        secure=False,  # Cambiar a True en producción
        samesite='lax'
    )

    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response