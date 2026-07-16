import pytest

from app.rbac import PERMISSIONS, Role, can

print(PERMISSIONS)


@pytest.mark.parametrize(
    "role,resource,action,expected",
    [
        # Admin can do everything
        (Role.ADMIN, "project", "create", True),
        (Role.ADMIN, "project", "delete", True),
        (Role.ADMIN, "project", "archive", True),
        (Role.ADMIN, "project", "add_member", True),
        (Role.ADMIN, "task", "create", True),
        (Role.ADMIN, "task", "assign", True),
        (Role.ADMIN, "task", "update_status", True),
        (Role.ADMIN, "task", "update_priority", True),
        (Role.ADMIN, "task", "delete", True),
        (Role.ADMIN, "project", "read", True),
        (Role.ADMIN, "task", "read", True),
        (Role.ADMIN, "comment", "create", True),
        (Role.ADMIN, "comment", "delete", True),
        (Role.ADMIN, "audit", "read", True),
        # Editor can create/edit own posts but not manage tags or delete any comment
        (Role.EDITOR, "project", "create", True),
        (Role.EDITOR, "project", "delete", True),
        (Role.EDITOR, "project", "archive", True),
        (Role.EDITOR, "project", "add_member", True),
        (Role.EDITOR, "task", "create", True),
        (Role.EDITOR, "task", "assign", True),
        (Role.EDITOR, "task", "update_status", True),
        (Role.EDITOR, "task", "update_priority", True),
        (Role.EDITOR, "task", "delete", True),
        (Role.EDITOR, "project", "read", True),
        (Role.EDITOR, "task", "read", True),
        (Role.EDITOR, "comment", "create", True),
        (Role.EDITOR, "comment", "delete", True),
        # Viewer is read-only for posts, can comment
        (Role.VIEWER, "project", "create", False),
        (Role.VIEWER, "project", "delete", False),
        (Role.VIEWER, "project", "archive", False),
        (Role.VIEWER, "project", "add_member", False),
        (Role.VIEWER, "task", "create", False),
        (Role.VIEWER, "task", "assign", False),
        (Role.VIEWER, "task", "update_status", False),
        (Role.VIEWER, "task", "update_priority", False),
        (Role.VIEWER, "task", "delete", False),
        (Role.VIEWER, "comment", "create", True),
        (Role.VIEWER, "comment", "delete", True),
        (Role.VIEWER, "project", "read", True),
        (Role.VIEWER, "task", "read", True),
        (Role.VIEWER, "comment", "create", True),
        (Role.VIEWER, "comment", "delete", True),
    ],
)
def test_permission_matrix(role, resource, action, expected):
    assert can(role, resource, action) == expected
