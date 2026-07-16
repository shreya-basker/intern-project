"""import pytest

@pytest.mark.parametrize("role,method,path,expected_status", [
    # Posts
    ("viewer",  "POST",   "/posts",        403),
    ("editor",  "POST",   "/posts",        201),
    ("admin",   "POST",   "/posts",        201),
    # Tags
    ("viewer",  "POST",   "/tags",         403),
    ("editor",  "POST",   "/tags",         403),
    ("admin",   "POST",   "/tags",         201),
    # Users — delete
    ("viewer",  "DELETE", "/users/99",     403),
    ("editor",  "DELETE", "/users/99",     403),
    ("admin",   "DELETE", "/users/99",     204),
    # Audit log
    ("viewer",  "GET",    "/admin/audit-logs", 403),
    ("editor",  "GET",    "/admin/audit-logs", 403),
    ("admin",   "GET",    "/admin/audit-logs", 200),
])
async def test_rbac_matrix(client, role, method, path, expected_status, db_session):
    # Override current user based on role
    from app.dependencies import get_current_user
    from app.models import User
    from app.main import app
    fake_user = User(id=1, name="Test", email="t@t.com",
                      hashed_password="x", role=role)
    app.dependency_overrides[get_current_user] = lambda: fake_user
    response = await getattr(client, method.lower())(path, json={})
    assert response.status_code == expected_status
    app.dependency_overrides.clear()

"""
