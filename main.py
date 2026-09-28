from datetime import date as Date
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
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

@app.get('/transactions/filter', response_model=list[TransactionResponse])
def filter_transactions(
    user: user_dependency,
    db : db_dependency,
    type : Optional[Literal["income", "expense"]] = None,
    category : Optional[str] = None,
    minimum_amount : Optional[float] = None,
    maximum_amount : Optional[float] = None,
):

    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    query = db.query(models.Transaction).filter(models.Transaction.owner_id == user.id)

    if type is not None:
        query = query.filter(models.Transaction.type == type)

    if category is not None:
        query = query.filter(models.Transaction.category == category)

    if minimum_amount is not None:
        query = query.filter(models.Transaction.amount >= minimum_amount)

    if maximum_amount is not None:
        query = query.filter(models.Transaction.amount <= maximum_amount)

    return query.all()

@app.get('/transactions/{transaction_id}', response_model=TransactionResponse)
def read_specific_transaction(user: user_dependency, db : db_dependency, transaction_id : int):

    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    specific_transaction = db.query(models.Transaction).filter(models.Transaction.owner_id == user.id).filter(models.Transaction.id == transaction_id).first()
    if specific_transaction is not None:
        return specific_transaction
    else:
        raise HTTPException(status_code=404, detail='Transaction not found')

@app.post('/transactions', response_model=TransactionResponse, status_code=201)
def create_transaction(user: user_dependency, db : db_dependency, new_transaction : Transaction):

    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    transaction_model = models.Transaction(**new_transaction.model_dump(), owner_id = user.id)
    db.add(transaction_model)
    db.commit()
    db.refresh(transaction_model)

    return transaction_model

@app.put('/transactions/{transaction_id}', response_model=TransactionResponse)
def update_transaction(user: user_dependency, db : db_dependency, transaction_id : int, update_transaction : TransactionUpdate):

    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    transaction = db.query(models.Transaction).filter(models.Transaction.owner_id == user.id).filter(models.Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail='Transaction not found')

    update_data = update_transaction.model_dump(exclude_unset=True)

    for key,value in update_data.items():
        setattr(transaction,key,value)

    db.commit()
    db.refresh(transaction)

    return transaction

@app.delete('/transactions/{transaction_id}')
def delete_transaction(user: user_dependency, db : db_dependency, transaction_id : int):

    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    transaction = db.query(models.Transaction).filter(models.Transaction.owner_id == user.id).filter(models.Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail='Transaction not found')

    db.query(models.Transaction).filter(models.Transaction.owner_id == user.id).filter(models.Transaction.id == transaction_id).delete()

    db.commit()
    return JSONResponse(status_code=200, content={'message' : 'Transaction deleted successfully'})
