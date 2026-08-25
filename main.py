from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Task as TaskModel, User as UserModel, Project as ProjectModel
from security import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import engine, Base, get_db
from models import Task as TaskModel


Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        user_id = decode_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(UserModel).filter(
        UserModel.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user

def require_roles(*allowed_roles: str):
    def role_checker(
        current_user: UserModel = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission"
            )

        return current_user

    return role_checker

class TaskCreate(BaseModel):
    title: str
    description: str


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "USER"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ProjectCreate(BaseModel):
    name: str
    description: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    created_by: int

    class Config:
        from_attributes = True

@app.get("/")
def home():
    return {
        "message": "Team Management API"
    }


@app.post("/tasks", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    new_task = TaskModel(
        title=task.title,
        description=task.description
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db)
):
    tasks = db.query(TaskModel).all()

    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    task.title = task_data.title
    task.description = task_data.description

    db.commit()
    db.refresh(task)

    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }

@app.post("/auth/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(UserModel).filter(
        UserModel.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = UserModel(
    name=user_data.name,
    email=user_data.email,
    password_hash=hash_password(user_data.password),
    role="USER"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/auth/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(
        UserModel.email == login_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/auth/me", response_model=UserResponse)
def get_me(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user

@app.get("/admin/test")
def admin_test(
    current_user: UserModel = Depends(
        require_roles("ADMIN", "MANAGER")
    )
):
    return {
        "message": "You have access",
        "user": current_user.name,
        "role": current_user.role
    }

@app.post(
    "/projects",
    response_model=ProjectResponse
)
def create_project(
    project_data: ProjectCreate,
    current_user: UserModel = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
    db: Session = Depends(get_db)
):
    new_project = ProjectModel(
        name=project_data.name,
        description=project_data.description,
        created_by=current_user.id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project