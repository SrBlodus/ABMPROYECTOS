from sqlalchemy.orm import Session
from sqlalchemy import text

def set_audit_user(db: Session, user_id: int):
    """Establece el ID del usuario actual para la auditoría"""
    try:
        db.execute(text("SET @user_id = :user_id"), {"user_id": user_id})
    except Exception as e:
        print(f"Error al establecer usuario de auditoría: {str(e)}")