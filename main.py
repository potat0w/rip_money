from datetime import date as Date
from typing import Optional, Literal
from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict
import models
from database import engine
from router import auth

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
