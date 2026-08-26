from fastapi import FastAPI

from .routers import auth, tasks, projects, dashboard

from app.routers.users import router as users_router

app = FastAPI(
    title="Team Management API"
)


app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(dashboard.router)
app.include_router(users_router)

@app.get("/")
def home():
    return {
        "message": "Team Management API"
    }