from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status

from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

# 💡 Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔐 Endpoints
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_id: int = Path(gt=0)
):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    
    db.delete(todo_model)
    db.commit()
