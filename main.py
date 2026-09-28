from datetime import date as Date
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
import models
from database import engine
from router import auth
from router.auth import user_dependency, db_dependency

app = FastAPI(
    title="Personal Expense Tracker API",
    description="A simple API to track personal expenses"
)

class Transaction(BaseModel):
    title : str
    amount : float = Field(gt=0)
    type : Literal["income", "expense"]
    category : str
    date : Date

class TransactionUpdate(BaseModel):
    title : Optional[str] = Field(default=None)
    amount : Optional[float] = Field(default=None, gt=0)
    type : Optional[Literal["income", "expense"]] = None
    category : Optional[str] = Field(default=None)
    date : Optional[Date] = Field(default=None)

class TransactionResponse(BaseModel):
    id : int
    title : str
    amount : float
    type : str
    category : str
    date : Date
    owner_id : int
    model_config = ConfigDict(from_attributes=True)

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Personal Expense Tracker API is running"}

@app.get('/transactions', response_model=list[TransactionResponse])
def read_transactions(user: user_dependency, db : db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    return db.query(models.Transaction).filter(models.Transaction.owner_id == user.id).all()

@app.post('/transactions', response_model=TransactionResponse, status_code=201)
def create_transaction(user: user_dependency, db : db_dependency, new_transaction : Transaction):

    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    transaction_model = models.Transaction(**new_transaction.model_dump(), owner_id = user.id)
    db.add(transaction_model)
    db.commit()
    db.refresh(transaction_model)

    return transaction_model
