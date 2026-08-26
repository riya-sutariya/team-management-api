from app.models import Project, Task


def test_task_ownership(
    client,
    db,
    create_user,
    get_token
):
    riya = create_user(
        "Riya",
        "riya@example.com"
    )

    john = create_user(
        "John",
        "john@example.com"
    )

    project = Project(
        name="Website",
        description="Company website",
        created_by=riya.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task = Task(
        title="Build Login",
        description="Create login page",
        project_id=project.id,
        assigned_to=riya.id,
        status="TODO",
        priority="HIGH"
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    # Riya owns the task → should be allowed
    riya_token = get_token(
        "riya@example.com",
        "password123"
    )

    response = client.put(
        f"/tasks/{task.id}/status",
        params={
            "status": "IN_PROGRESS"
        },
        headers={
            "Authorization": f"Bearer {riya_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"

    # John does not own the task → should be forbidden
    john_token = get_token(
        "john@example.com",
        "password123"
    )

    response = client.put(
        f"/tasks/{task.id}/status",
        params={
            "status": "DONE"
        },
        headers={
            "Authorization": f"Bearer {john_token}"
        }
    )

    assert response.status_code == 403