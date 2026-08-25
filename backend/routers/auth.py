"""
LearnLens AI - Authentication Router
POST /auth/login
POST /auth/register
GET  /auth/me
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user(token: str, db: Session) -> models.User:
    """Decode JWT and fetch current user."""
    from auth import decode_access_token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(models.User).filter(models.User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(models.User).filter(
        (models.User.username == credentials.username) |
        (models.User.email == credentials.username)
    ).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    token = create_access_token(data={"sub": user.username, "role": user.role, "user_id": user.id})
    
    return schemas.Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
    )


@router.post("/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    user = models.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
    )
    db.add(user)
    db.flush()
    
    # Create associated profile
    if user_data.role == "student":
        profile = models.StudentProfile(user_id=user.id, enrolled_subjects=[])
        db.add(profile)
    elif user_data.role == "teacher":
        profile = models.TeacherProfile(user_id=user.id)
        db.add(profile)
    
    db.commit()
    db.refresh(user)
    
    token = create_access_token(data={"sub": user.username, "role": user.role, "user_id": user.id})
    return schemas.Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
    )
