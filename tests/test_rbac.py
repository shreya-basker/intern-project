import pytest

from week4.app.rbac import PERMISSIONS, Role, can

print(PERMISSIONS)


@pytest.mark.parametrize(
    "role,resource,action,expected",
    [
        # Admin can do everything
        (Role.ADMIN, "post", "create", True),
        (Role.ADMIN, "post", "delete_any", True),
        (Role.ADMIN, "tag", "manage", True),
        (Role.ADMIN, "audit", "read", True),
        # Editor can create/edit own posts but not manage tags or delete any comment
        (Role.EDITOR, "post", "create", True),
        (Role.EDITOR, "post", "update_own", True),
        (Role.EDITOR, "post", "update_any", False),
        (Role.EDITOR, "tag", "manage", False),
        (Role.EDITOR, "comment", "delete_any", False),
        # Viewer is read-only for posts, can comment
        (Role.VIEWER, "post", "read", True),
        (Role.VIEWER, "post", "create", False),
        (Role.VIEWER, "comment", "create", True),
        (Role.VIEWER, "tag", "manage", False),
        (Role.VIEWER, "audit", "read", False),
    ],
)
def test_permission_matrix(role, resource, action, expected):
    assert can(role, resource, action) == expected
