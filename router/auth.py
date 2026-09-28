from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import User
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

router = APIRouter(prefix='/auth')

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class CreateUser(BaseModel):
    username : str
    email : EmailStr
    password : str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post('/register')
def register_user(db : db_dependency, new_user : CreateUser):

    existing_username = db.query(User).filter(User.username == new_user.username).first()
    if existing_username is not None:
        raise HTTPException(status_code=400, detail='Username already exists')

    existing_email = db.query(User).filter(User.email == new_user.email).first()
    if existing_email is not None:
        raise HTTPException(status_code=400, detail='Email already exists')

    user_model = User(
        username = new_user.username,
        email = new_user.email,
        hashed_password = bcrypt_context.hash(new_user.password),
    )

    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    return JSONResponse(
        status_code=201,
        content={
            'id': user_model.id,
            'username': user_model.username,
            'email': user_model.email,
        },
    )
