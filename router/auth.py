import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Annotated
from database import SessionLocal
from models import User
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix='/auth')

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'

class CreateUser(BaseModel):
    username : str
    email : EmailStr
    password : str

def authenticate_user(username, password, db):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return False
    if bcrypt_context.verify(password, user.hashed_password):
        return user
    return False

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

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

@router.post('/login')
def login_user(db : db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    token = create_access_token(user.username, user.id, timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}
