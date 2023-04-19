from typing import Optional, Annotated

from starlette import status

from models import Todos
from fastapi import APIRouter, Depends, Path
from starlette.exceptions import HTTPException
from routers import auth
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

router = APIRouter()



def get_db():
    db = SessionLocal()
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6, description="The priority must be between 1-5")
    complete: bool

@router.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@router.get("/todo/{todo_id}")
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is not None:
        return todo_model
    http_exception()


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(todo_request: TodoRequest, db: db_dependency):
    todo_model = Todos(**todo_request.dict())

    db.add(todo_model)
    db.commit()

    return successful_response(201)


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,
                       todo_request: TodoRequest,
                       todo_id: int = Path(gt=0)):

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise http_exception()

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

    return successful_response(200)

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0), ):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise http_exception()

    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

    return successful_response(200)


def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }

def http_exception():
    raise HTTPException(status_code=404, detail="Todo not found")