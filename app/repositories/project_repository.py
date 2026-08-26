from sqlalchemy.orm import Session

from ..models import Project


class ProjectRepository:

    def create(
        self,
        db: Session,
        name: str,
        description: str,
        created_by: int
    ) -> Project:
        project = Project(
            name=name,
            description=description,
            created_by=created_by
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    def get_by_id(
        self,
        db: Session,
        project_id: int
    ) -> Project | None:
        return db.query(Project).filter(
            Project.id == project_id
        ).first()

    def get_all(
        self,
        db: Session
    ) -> list[Project]:
        return db.query(Project).all()

    def update(
        self,
        db: Session,
        project: Project,
        name: str,
        description: str
    ) -> Project:
        project.name = name
        project.description = description

        db.commit()
        db.refresh(project)

        return project

    def delete(
        self,
        db: Session,
        project: Project
    ) -> None:
        db.delete(project)
        db.commit()
        