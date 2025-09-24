from fastapi import FastAPI

from routes.users import router as user_router
from routes.companies import router as companies_router
from routes.auth import router as auth_router
from routes.tasks import router as tasks_router

app = FastAPI()

app.include_router(user_router)
app.include_router(companies_router)
app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/")
def root():
    return {"message": "Hello, World!"}
