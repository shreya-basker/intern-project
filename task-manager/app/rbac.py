from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


# app/rbac.py

PERMISSIONS = {
    # Projects
    ("project", "create"): {"admin", "editor"},
    ("project", "delete"): {"admin", "editor"},
    ("project", "archive"): {"admin", "editor"},
    ("project", "add_member"): {"admin", "editor"},
    # Tasks
    ("task", "create"): {"admin", "editor"},
    ("task", "assign"): {"admin", "editor"},
    ("task", "update_status"): {"admin", "editor"},
    ("task", "update_priority"): {"admin", "editor"},
    ("task", "delete"): {"admin", "editor"},
    # Reading
    ("project", "read"): {"admin", "editor", "viewer"},
    ("task", "read"): {"admin", "editor", "viewer"},
    # Comments
    ("comment", "create"): {"admin", "editor", "viewer"},
    ("comment", "delete"): {"admin", "editor", "viewer"},
    # Audit
    ("audit", "read"): {"admin"},
}


def can(user_role: str, resource: str, action: str) -> bool:
    return user_role in PERMISSIONS.get((resource, action), set())
