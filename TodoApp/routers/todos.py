from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from starlette import status
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="TodoApp/templates")

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)

# 📦 DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📋 Pydantic model
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

###     Pages    ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: Session = Depends(get_db)):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        
        if user is None:
            return redirect_to_login()
        
        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

        return templates.TemplateResponse("todo.html", {
            "request": request,
            "todos": todos,
            "user": user
        })
    except:
        return redirect_to_login()
    

@router.get('/add-todo-page')
async def render_add_todo_page(request: Request, db: Session = Depends(get_db)):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        
        if user is None:
            return redirect_to_login()
        
        return templates.TemplateResponse("add_todo.html", {
            "request": request,
            "user": user
        })
    except:
        return redirect_to_login()
    

@router.get('/edit-todo-page/{todo_id}')
async def render_edit_todo_page(
    request: Request,
    db: Session = Depends(get_db),
    todo_id: int = Path(gt=0)
):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        
     
        if user is None:
            return redirect_to_login()
        
        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse("edit_todo.html", {
            "request": request,
            "todo": todo,
            "user": user
        })
    
    except:
        return redirect_to_login()
    


# 🧾 Endpoints
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_request: TodoRequest,  # 👈 ya no uses Depends() acá
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = Todos(**todo_request.dict(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_request: TodoRequest = Depends(),
    todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail='Todo not found.')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail='Todo not found.')

    db.delete(todo_model)
    db.commit()
