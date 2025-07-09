from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status
from passlib.context import CryptContext

from ..models import Users
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(prefix='/user', tags=['user'])

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# 📦 DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📋 Pydantic schema
class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

# 🧾 Endpoints
@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_verification: UserVerification = Depends()
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phonenumber(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    phone_number: str = Path(...)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
