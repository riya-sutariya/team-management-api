from sqlalchemy.orm import Session

from ..models import Task
from ..repositories.task_repository import TaskRepository


class TaskService:

    def __init__(self):
        self.repository = TaskRepository()

    def get_task(
        self,
        db: Session,
        task_id: int
    ) -> Task | None:
        return self.repository.get_by_id(
            db,
            task_id
        )

    def create_task(
        self,
        db: Session,
        task: Task
    ) -> Task:
        return self.repository.create(
            db,
            task
        )

    def update_task(
        self,
        db: Session,
        task: Task
    ) -> Task:
        return self.repository.update(
            db,
            task
        )