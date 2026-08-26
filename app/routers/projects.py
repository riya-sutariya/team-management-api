from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Project as ProjectModel
from ..models import User as UserModel
from ..schemas import ProjectCreate, ProjectResponse
from ..dependencies import (
    get_current_user,
    require_permission
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post("/", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    current_user: UserModel = Depends(
        require_permission("projects.create")
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


@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    current_user: UserModel = Depends(
        require_permission("projects.read")
    ),
    db: Session = Depends(get_db)
):
    return db.query(ProjectModel).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: UserModel = Depends(
        require_permission("projects.read")
    ),
    db: Session = Depends(get_db)
):
    project = db.query(ProjectModel).filter(
        ProjectModel.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
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
    project = db.query(ProjectModel).filter(
        ProjectModel.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    project.name = project_data.name
    project.description = project_data.description

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: UserModel = Depends(
        require_permission("projects.delete")
    ),
    db: Session = Depends(get_db)
):
    project = db.query(ProjectModel).filter(
        ProjectModel.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }