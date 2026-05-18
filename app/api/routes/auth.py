from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.security import hash_password, verify_password, create_access_token
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
def register(payload: RegisterRequest):
    db = SessionLocal()
    try:
        existing = db.execute(select(User).where(User.email == payload.email)).scalars().first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(email=payload.email, hashed_password=hash_password(payload.password))
        db.add(user)
        db.commit()
        return {"message": "User created"}
    finally:
        db.close()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    db = SessionLocal()
    try:
        user = db.execute(select(User).where(User.email == payload.email)).scalars().first()
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(subject=user.email)
        return TokenResponse(access_token=token)
    finally:
        db.close()