from fastapi import FastAPI
import models
from database import engine

app = FastAPI(
    title="Personal Expense Tracker API",
    description="A simple API to track personal expenses",
    version="1.0.0",
)

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Personal Expense Tracker API is running"}
