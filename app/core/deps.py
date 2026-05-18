from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == sub).first()
        if not user:
            # token válido mas usuário inexistente
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")
        return user
    finally:
        db.close()