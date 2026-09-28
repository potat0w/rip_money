from fastapi import FastAPI

app = FastAPI(
    title="Personal Expense Tracker API",
    description="A simple API to track personal expenses",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Personal Expense Tracker API is running"}
