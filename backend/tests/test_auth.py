"""
DocuForge AI — Authentication & Production Deployment Tests
Covers:
- Login with existing accounts
- Login with invalid password (401)
- Login with nonexistent email (401)
- Case-insensitive email login
- User registration and duplicate prevention
- Refresh token rotation
- Protected /api/auth/me route with/without Bearer token
- Logout endpoint
- Production CORS origin handling (https://docu-forge-nine.vercel.app & preview regex)
- Health endpoints (/ and /api/health)
"""
import sys
from pathlib import Path

# Ensure backend package is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash, create_access_token, create_refresh_token


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestAuthenticationEndpoints:
    """Test suite for all authentication flows."""

    def test_login_nonexistent_email(self, client):
        """Nonexistent email must return 401 Unauthorized, never 404 or 500."""
        res = client.post("/api/auth/login", json={
            "email": "definitely_nonexistent_user_999@example.com",
            "password": "AnyPassword123!"
        })
        assert res.status_code == 401
        data = res.json()
        assert "Invalid email or password." in data.get("detail", "")

    def test_login_incorrect_password(self, client):
        """Existing email with wrong password must return 401 Unauthorized."""
        res = client.post("/api/auth/login", json={
            "email": "dhruvwadhwa8661@gmail.com",
            "password": "WrongPassword999!"
        })
        assert res.status_code == 401
        data = res.json()
        assert "Invalid email or password." in data.get("detail", "")

    def test_register_and_login_lifecycle(self, client, db_session):
        """Register a test user, log in, verify tokens, test casing, and clean up."""
        test_email = "authtest_user_suite@example.com"

        # Clean up in case of previous run
        existing = db_session.query(User).filter(User.email == test_email).first()
        if existing:
            db_session.delete(existing)
            db_session.commit()

        # 1. Register new user
        reg_res = client.post("/api/auth/register", json={
            "email": test_email,
            "full_name": "Auth Test User",
            "password": "SecurePassword123!",
            "organization": "DocuForge QA"
        })
        assert reg_res.status_code == 201
        reg_data = reg_res.json()
        assert "access_token" in reg_data
        assert "refresh_token" in reg_data
        assert reg_data["user"]["email"] == test_email

        # 2. Duplicate registration must return 400
        dup_res = client.post("/api/auth/register", json={
            "email": test_email,
            "full_name": "Duplicate User",
            "password": "AnotherPassword123!"
        })
        assert dup_res.status_code == 400
        assert "already exists" in dup_res.json().get("detail", "")

        # 3. Login with matching credentials
        login_res = client.post("/api/auth/login", json={
            "email": test_email,
            "password": "SecurePassword123!"
        })
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert "access_token" in login_data
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        # 4. Login with uppercase email (case-insensitivity test)
        upper_login_res = client.post("/api/auth/login", json={
            "email": test_email.upper(),
            "password": "SecurePassword123!"
        })
        assert upper_login_res.status_code == 200

        # 5. Access /api/auth/me with access token
        me_res = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {access_token}"
        })
        assert me_res.status_code == 200
        assert me_res.json()["email"] == test_email

        # 6. Access /api/auth/me without token must return 401 or 403
        no_auth_res = client.get("/api/auth/me")
        assert no_auth_res.status_code in [401, 403]

        # 7. Refresh token flow
        refresh_res = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh_res.status_code == 200
        new_tokens = refresh_res.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens

        # 8. Refresh token with invalid token must return 401
        bad_refresh_res = client.post("/api/auth/refresh", json={
            "refresh_token": "totally.invalid.token"
        })
        assert bad_refresh_res.status_code == 401

        # 9. Logout endpoint
        logout_res = client.post("/api/auth/logout")
        assert logout_res.status_code == 200
        assert "logged out" in logout_res.json().get("message", "").lower()

        # Clean up test user
        user = db_session.query(User).filter(User.email == test_email).first()
        if user:
            db_session.delete(user)
            db_session.commit()


class TestProductionCORSAndHealth:
    """Test CORS headers and health endpoints for Vercel production deployment."""

    def test_health_endpoints(self, client):
        """Both / and /api/health must return healthy 200 status."""
        for path in ["/", "/api/health"]:
            res = client.get(path)
            assert res.status_code == 200
            data = res.json()
            assert data.get("status") == "healthy"

    def test_cors_options_preflight_production_vercel(self, client):
        """OPTIONS preflight from https://docu-forge-nine.vercel.app must succeed with CORS headers."""
        res = client.options("/api/auth/login", headers={
            "Origin": "https://docu-forge-nine.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization"
        })
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == "https://docu-forge-nine.vercel.app"
        assert res.headers.get("access-control-allow-credentials") == "true"

    def test_cors_options_preflight_preview_vercel(self, client):
        """OPTIONS preflight from any Vercel preview domain must be allowed via regex."""
        preview_origin = "https://docuforge-git-preview-ethnix.vercel.app"
        res = client.options("/api/auth/login", headers={
            "Origin": preview_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization"
        })
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == preview_origin
        assert res.headers.get("access-control-allow-credentials") == "true"

    def test_cors_get_production_origin(self, client):
        """Direct GET request with production Origin header returns access-control-allow-origin."""
        res = client.get("/api/health", headers={
            "Origin": "https://docu-forge-nine.vercel.app"
        })
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == "https://docu-forge-nine.vercel.app"
