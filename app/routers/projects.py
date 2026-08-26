from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Project as ProjectModel,
    User as UserModel
)
from ..schemas import ProjectCreate, ProjectResponse
from ..dependencies import (
    get_current_user,
    require_permission
)
from ..services.project_service import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

project_service = ProjectService()


@router.post("/", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    current_user: UserModel = Depends(
        require_permission("projects.create")
    ),
    db: Session = Depends(get_db)
):
    return project_service.create_project(
        db=db,
        name=project_data.name,
        description=project_data.description,
        created_by=current_user.id
    )


@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    current_user: UserModel = Depends(
        require_permission("projects.read")
    ),
    db: Session = Depends(get_db)
):
    projects = project_service.get_projects(db)

    if current_user.role in ["ADMIN", "MANAGER"]:
        return projects

    return [
        project
        for project in projects
        if current_user in project.members
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = project_service.get_project(
        db,
        project_id
    )

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

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectCreate,
    current_user: UserModel = Depends(
        require_permission("projects.update")
    ),
    db: Session = Depends(get_db)
):
    project = project_service.get_project(
        db,
        project_id
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return project_service.update_project(
        db=db,
        project=project,
        name=project_data.name,
        description=project_data.description
    )


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: UserModel = Depends(
        require_permission("projects.delete")
    ),
    db: Session = Depends(get_db)
):
    project = project_service.get_project(
        db,
        project_id
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    project_service.delete_project(
        db,
        project
    )

    return {
        "message": "Project deleted successfully"
    }


# -------------------------
# Project Membership
# -------------------------


@router.post("/{project_id}/members/{user_id}")
def add_project_member(
    project_id: int,
    user_id: int,
    current_user: UserModel = Depends(
        require_permission("projects.update")
    ),
    db: Session = Depends(get_db)
):
    project = project_service.get_project(
        db,
        project_id
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    user = db.query(UserModel).filter(
        UserModel.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user in project.members:
        raise HTTPException(
            status_code=400,
            detail="User is already a project member"
        )

    project.members.append(user)

    db.commit()

    return {
        "message": "User added to project"
    }


@router.get("/{project_id}/members")
def get_project_members(
    project_id: int,
    current_user: UserModel = Depends(
        require_permission("projects.read")
    ),
    db: Session = Depends(get_db)
):
    project = project_service.get_project(
        db,
        project_id
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
        for user in project.members
    ]


@router.delete("/{project_id}/members/{user_id}")
def remove_project_member(
    project_id: int,
    user_id: int,
    current_user: UserModel = Depends(
        require_permission("projects.update")
    ),
    db: Session = Depends(get_db)
):
    project = project_service.get_project(
        db,
        project_id
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    user = db.query(UserModel).filter(
        UserModel.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user not in project.members:
        raise HTTPException(
            status_code=404,
            detail="User is not a member of this project"
        )

    project.members.remove(user)

    db.commit()

    return {
        "message": "User removed from project"
    }