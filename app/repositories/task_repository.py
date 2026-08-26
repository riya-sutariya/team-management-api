from sqlalchemy.orm import Session

from ..models import Task


class TaskRepository:

    def get_by_id(
        self,
        db: Session,
        task_id: int
    ) -> Task | None:
        return db.query(Task).filter(
            Task.id == task_id
        ).first()

    def get_all(
        self,
        db: Session,
        query
    ):
        return query

    def create(
        self,
        db: Session,
        task: Task
    ) -> Task:
        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    def update(
        self,
        db: Session,
        task: Task
    ) -> Task:
        db.commit()
        db.refresh(task)

        return task