from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from database import get_db
from models import User
from schemas import UserCreate, Token, UserOut

router = APIRouter()

# регистрация
@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# логин
@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# защищённый эндпоинт
@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
