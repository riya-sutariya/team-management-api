from math import ceil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Task as TaskModel,
    User as UserModel,
    Project as ProjectModel
)
from ..schemas import (
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskPriority,
    TaskListResponse
)
from ..dependencies import (
    get_current_user,
    require_permission
)
from ..services.task_service import TaskService


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

task_service = TaskService()


@router.get(
    "/",
    response_model=TaskListResponse
)
def get_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    current_user: UserModel = Depends(
        require_permission("tasks.read")
    ),
    db: Session = Depends(get_db)
):
    query = db.query(TaskModel)

    if current_user.role == "USER":
        query = query.join(
            ProjectModel,
            TaskModel.project_id == ProjectModel.id
        ).filter(
            ProjectModel.members.any(
                UserModel.id == current_user.id
            )
        )

    if status:
        query = query.filter(
            TaskModel.status == status.value
        )

    if priority:
        query = query.filter(
            TaskModel.priority == priority.value
        )

    total = query.count()

    pages = ceil(total / limit) if total else 0

    tasks = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    return {
        "items": tasks,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


@router.get(
    "/my",
    response_model=list[TaskResponse]
)
def get_my_tasks(
    current_user: UserModel = Depends(
        require_permission("tasks.read")
    ),
    db: Session = Depends(get_db)
):
    return db.query(TaskModel).filter(
        TaskModel.assigned_to == current_user.id
    ).all()


@router.post(
    "/",
    response_model=TaskResponse
)
def create_task(
    task: TaskCreate,
    current_user: UserModel = Depends(
        require_permission("tasks.create")
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

    return task_service.create_task(
        db,
        new_task
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(
    task_id: int,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    task = task_service.get_task(
        db,
        task_id
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    project = db.query(ProjectModel).filter(
        ProjectModel.id == task.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    if (
        current_user.role not in ["ADMIN", "MANAGER"]
        and current_user not in project.members
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this project"
        )

    return task


@router.put(
    "/{task_id}/status",
    response_model=TaskResponse
)
def update_my_task_status(
    task_id: int,
    status: TaskStatus,
    current_user: UserModel = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    task = task_service.get_task(
        db,
        task_id
    )

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

    return task_service.update_task(
        db,
        task
    )


@router.put(
    "/{task_id}/assign",
    response_model=TaskResponse
)
def assign_task(
    task_id: int,
    assigned_to: int,
    current_user: UserModel = Depends(
        require_permission("tasks.assign")
    ),
    db: Session = Depends(get_db)
):
    task = task_service.get_task(
        db,
        task_id
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    user = db.query(UserModel).filter(
        UserModel.id == assigned_to
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    task.assigned_to = assigned_to

    return task_service.update_task(
        db,
        task
    )