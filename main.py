from fastapi import FastAPI

from routes.user import router as user_router
from routes.companies import router as companies_router

app = FastAPI()

app.include_router(user_router)
app.include_router(companies_router)


@app.get("/")
def root():
    return {"message": "Hello, World!"}
