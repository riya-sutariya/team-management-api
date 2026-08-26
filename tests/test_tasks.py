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

def test_non_member_cannot_view_project_task(
    client,
    db,
    create_user,
    get_token
):
    admin = create_user(
        "Admin",
        "taskadmin@example.com",
        role="ADMIN"
    )

    riya = create_user(
        "Riya",
        "taskriya@example.com"
    )

    john = create_user(
        "John",
        "taskjohn@example.com"
    )

    project = Project(
        name="Private Project",
        description="Private tasks",
        created_by=admin.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    # Riya is a member
    project.members.append(riya)
    db.commit()

    task = Task(
        title="Private Task",
        description="Only project members",
        project_id=project.id,
        assigned_to=riya.id,
        status="TODO",
        priority="HIGH"
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    # John is NOT a member
    john_token = get_token(
        "taskjohn@example.com",
        "password123"
    )

    response = client.get(
        f"/tasks/{task.id}",
        headers={
            "Authorization": f"Bearer {john_token}"
        }
    )

    assert response.status_code == 403

def test_project_member_can_view_task(
    client,
    db,
    create_user,
    get_token
):
    admin = create_user(
        "Admin",
        "taskadmin2@example.com",
        role="ADMIN"
    )

    riya = create_user(
        "Riya",
        "taskriya2@example.com"
    )

    project = Project(
        name="Team Project",
        description="Team tasks",
        created_by=admin.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    project.members.append(riya)
    db.commit()

    task = Task(
        title="Team Task",
        description="Task for team",
        project_id=project.id,
        assigned_to=riya.id,
        status="TODO",
        priority="MEDIUM"
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    token = get_token(
        "taskriya2@example.com",
        "password123"
    )

    response = client.get(
        f"/tasks/{task.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == task.id

def test_task_pagination(
    client,
    db,
    create_user,
    get_token
):
    admin = create_user(
        "Admin",
        "pagination@example.com",
        role="ADMIN"
    )

    project = Project(
        name="Pagination Project",
        description="Testing pagination",
        created_by=admin.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    for i in range(5):
        task = Task(
            title=f"Task {i}",
            description="Pagination test",
            project_id=project.id,
            assigned_to=admin.id,
            status="TODO",
            priority="MEDIUM"
        )
        db.add(task)

    db.commit()

    token = get_token(
        "pagination@example.com",
        "password123"
    )

    response = client.get(
        "/tasks/?page=1&limit=2",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["pages"] == 3

def test_task_filtering(
    client,
    db,
    create_user,
    get_token
):
    admin = create_user(
        "Admin",
        "filter@example.com",
        role="ADMIN"
    )

    project = Project(
        name="Filter Project",
        description="Testing filters",
        created_by=admin.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    db.add_all([
        Task(
            title="Done Task",
            description="Test",
            project_id=project.id,
            assigned_to=admin.id,
            status="DONE",
            priority="HIGH"
        ),
        Task(
            title="Todo Task",
            description="Test",
            project_id=project.id,
            assigned_to=admin.id,
            status="TODO",
            priority="LOW"
        ),
    ])

    db.commit()

    token = get_token(
        "filter@example.com",
        "password123"
    )

    response = client.get(
        "/tasks/?status=DONE&priority=HIGH",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["title"] == "Done Task"