import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from backend.app.services.security import SecurityService, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    new_user = User(
        id=str(uuid.uuid4()),
        email=user_in.email,
        hashed_password=SecurityService.hash_password(user_in.password),
        full_name=user_in.full_name or user_in.email.split("@")[0],
        is_active=True,
        is_demo=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = SecurityService.create_access_token({"sub": new_user.id, "email": new_user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=TokenResponse)
def login(creds: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email).first()
    if not user or not SecurityService.verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = SecurityService.create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.post("/demo-session", response_model=TokenResponse)
def create_demo_session(db: Session = Depends(get_db)):
    from backend.app.services.demo_seeder import DEMO_USER_ID, seed_demo_data
    seed_demo_data(db)
    demo_user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    token = SecurityService.create_access_token({"sub": demo_user.id, "email": demo_user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(demo_user)
    )
