from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


PERMISSIONS: dict[tuple[str, str], set[str]] = {
    ("user", "read"): {Role.ADMIN, Role.EDITOR, Role.VIEWER},
    ("user", "update_own"): {Role.ADMIN, Role.EDITOR, Role.VIEWER},
    ("user", "update_any"): {Role.ADMIN},
    ("user", "delete"): {Role.ADMIN},
    ("post", "create"): {Role.ADMIN, Role.EDITOR},
    ("post", "read"): {Role.ADMIN, Role.EDITOR, Role.VIEWER},
    ("post", "update_own"): {Role.ADMIN, Role.EDITOR},
    ("post", "update_any"): {Role.ADMIN},
    ("post", "delete_own"): {Role.ADMIN, Role.EDITOR},
    ("post", "delete_any"): {Role.ADMIN},
    ("comment", "create"): {Role.ADMIN, Role.EDITOR, Role.VIEWER},
    ("comment", "read"): {Role.ADMIN, Role.EDITOR, Role.VIEWER},
    ("comment", "delete_own"): {Role.ADMIN, Role.EDITOR, Role.VIEWER},
    ("comment", "delete_any"): {Role.ADMIN},
    ("tag", "read"): {Role.ADMIN, Role.EDITOR, Role.VIEWER},
    ("tag", "manage"): {Role.ADMIN},
    ("audit", "read"): {Role.ADMIN},
}


def can(user_role: str, resource: str, action: str) -> bool:
    return user_role in PERMISSIONS.get((resource, action), set())
