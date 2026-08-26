from app.models import User, Project, Task
from app.security import hash_password


def test_admin_dashboard(client, db, get_token):
    admin = User(
        name="Admin",
        email="admin@example.com",
        password_hash=hash_password("password123"),
        role="ADMIN"
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    project = Project(
        name="Website",
        description="Website project",
        created_by=admin.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task1 = Task(
        title="Task 1",
        description="First task",
        project_id=project.id,
        assigned_to=admin.id,
        status="DONE",
        priority="HIGH"
    )

    task2 = Task(
        title="Task 2",
        description="Second task",
        project_id=project.id,
        assigned_to=admin.id,
        status="TODO",
        priority="MEDIUM"
    )

    db.add_all([task1, task2])
    db.commit()

    token = get_token(
        "admin@example.com",
        "password123"
    )

    response = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_projects"] == 1
    assert data["total_tasks"] == 2
    assert data["completed_tasks"] == 1
    assert data["todo_tasks"] == 1
    assert data["in_progress_tasks"] == 0
    assert data["pending_tasks"] == 1


def test_user_dashboard_only_sees_own_tasks(
    client,
    db,
    get_token
):
    user1 = User(
        name="Riya",
        email="riya@example.com",
        password_hash=hash_password("password123"),
        role="USER"
    )

    user2 = User(
        name="John",
        email="john@example.com",
        password_hash=hash_password("password123"),
        role="USER"
    )

    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    project = Project(
        name="Website",
        description="Website project",
        created_by=user1.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task1 = Task(
        title="Riya Task",
        description="Task for Riya",
        project_id=project.id,
        assigned_to=user1.id,
        status="TODO",
        priority="HIGH"
    )

    task2 = Task(
        title="John Task",
        description="Task for John",
        project_id=project.id,
        assigned_to=user2.id,
        status="DONE",
        priority="LOW"
    )

    db.add_all([task1, task2])
    db.commit()

    token = get_token(
        "riya@example.com",
        "password123"
    )

    response = client.get(
        "/dashboard/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_tasks"] == 1
    assert data["todo_tasks"] == 1
    assert data["completed_tasks"] == 0
    assert data["pending_tasks"] == 1