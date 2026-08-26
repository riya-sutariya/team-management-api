from sqlalchemy.orm import Session

from ..models import Project
from ..repositories.project_repository import ProjectRepository


class ProjectService:

    def __init__(self):
        self.repository = ProjectRepository()

    def create_project(
        self,
        db: Session,
        name: str,
        description: str,
        created_by: int
    ) -> Project:
        return self.repository.create(
            db=db,
            name=name,
            description=description,
            created_by=created_by
        )

    def get_project(
        self,
        db: Session,
        project_id: int
    ) -> Project | None:
        return self.repository.get_by_id(
            db,
            project_id
        )

    def get_projects(
        self,
        db: Session
    ) -> list[Project]:
        return self.repository.get_all(db)

    def update_project(
        self,
        db: Session,
        project: Project,
        name: str,
        description: str
    ) -> Project:
        return self.repository.update(
            db=db,
            project=project,
            name=name,
            description=description
        )

    def delete_project(
        self,
        db: Session,
        project: Project
    ) -> None:
        self.repository.delete(
            db,
            project
        )