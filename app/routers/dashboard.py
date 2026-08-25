from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Task as TaskModel, Project as ProjectModel, User as UserModel
from ..schemas import DashboardResponse
from ..dependencies import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/", response_model=DashboardResponse)
def dashboard(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role in ["ADMIN", "MANAGER"]:
        task_query = db.query(TaskModel)
        total_projects = db.query(ProjectModel).count()

    else:
        task_query = db.query(TaskModel).filter(
            TaskModel.assigned_to == current_user.id
        )
        total_projects = 0

    total_tasks = task_query.count()

    completed_tasks = task_query.filter(
        TaskModel.status == "DONE"
    ).count()

    todo_tasks = task_query.filter(
        TaskModel.status == "TODO"
    ).count()

    in_progress_tasks = task_query.filter(
        TaskModel.status == "IN_PROGRESS"
    ).count()

    pending_tasks = todo_tasks + in_progress_tasks

    return {
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "todo_tasks": todo_tasks,
        "in_progress_tasks": in_progress_tasks
    }