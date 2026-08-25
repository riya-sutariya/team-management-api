from fastapi import FastAPI

from .database import engine, Base
from . import models

from .routers import auth, tasks, projects, dashboard


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Team Management API"
)


app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(dashboard.router)

@app.get("/")
def home():
    return {
        "message": "Team Management API"
    }