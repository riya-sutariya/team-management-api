PERMISSIONS = {
    "ADMIN": {
        "users.read",
        "users.create",
        "users.update",
        "users.delete",

        "projects.read",
        "projects.create",
        "projects.update",
        "projects.delete",

        "tasks.read",
        "tasks.create",
        "tasks.update",
        "tasks.delete",
        "tasks.assign",
    },

    "MANAGER": {
        "projects.read",
        "projects.create",
        "projects.update",

        "tasks.read",
        "tasks.create",
        "tasks.update",
        "tasks.assign",
    },

    "USER": {
        "projects.read",

        "tasks.read",
        "tasks.update_own",
    },
}