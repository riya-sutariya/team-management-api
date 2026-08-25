from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Task as TaskModel, User as UserModel, Project as ProjectModel
from ..schemas import TaskCreate, TaskResponse, TaskStatus
from ..dependencies import get_current_user, require_roles


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.get("/my", response_model=list[TaskResponse])
def get_my_tasks(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(TaskModel).filter(
        TaskModel.assigned_to == current_user.id
    ).all()


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(TaskModel).all()


@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    current_user: UserModel = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
    db: Session = Depends(get_db)
):
    project = db.query(ProjectModel).filter(
        ProjectModel.id == task.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    user = db.query(UserModel).filter(
        UserModel.id == task.assigned_to
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    new_task = TaskModel(
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        assigned_to=task.assigned_to,
        status=task.status.value,
        priority=task.priority.value
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: UserModel = Depends(get_current_user),
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


@router.put("/{task_id}/status", response_model=TaskResponse)
def update_my_task_status(
    task_id: int,
    status: TaskStatus,
    current_user: UserModel = Depends(get_current_user),
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

    if task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own tasks"
        )

    task.status = status.value

    db.commit()
    db.refresh(task)

    return task