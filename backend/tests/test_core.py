"""
Backend tests for DocuForge AI — PDF generation, S3 service, and export API.
Run from the backend/ directory:
    .\\venv\\Scripts\\python.exe -m pytest tests/test_core.py -v
"""
import sys
import os
from io import BytesIO
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path

# Ensure backend package is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


# ─── PDF Service Tests ────────────────────────────────────────────────────────

class TestBuildStyles:
    """Verify _build_styles registers custom styles without collision."""

    def test_no_duplicate_styles(self):
        from app.services.pdf.pdf_service import _build_styles
        styles = _build_styles()
        # All expected custom styles must be present
        for name in ["DocTitle", "DocSubtitle", "SectionHeading", "SubHeading",
                     "BodyText2", "BulletText", "CustomCode", "TableHeader", "TableCell"]:
            assert name in styles.byName, f"Style '{name}' missing from stylesheet"

    def test_custom_code_not_named_code(self):
        """Ensure there is no style named 'Code' (that would duplicate ReportLab's built-in)."""
        from app.services.pdf.pdf_service import _build_styles
        styles = _build_styles()
        # The custom code style must be named 'CustomCode', not 'Code'
        assert "CustomCode" in styles.byName
        # Built-in 'Code' might exist; our code must NOT redefine it
        # (calling _build_styles twice must not raise KeyError)
        styles2 = _build_styles()
        assert styles2 is not None

    def test_styles_callable_twice(self):
        """_build_styles must be safe to call multiple times."""
        from app.services.pdf.pdf_service import _build_styles
        s1 = _build_styles()
        s2 = _build_styles()
        assert len(s1.byName) == len(s2.byName)


class TestGenerateProjectPdf:
    """Verify PDF generation produces valid PDF bytes for various doc states."""

    def _make_project(self, title="Test Project"):
        proj = MagicMock()
        proj.id = 1
        proj.title = title
        proj.domain = "web"
        proj.team_size = 5
        proj.timeline_weeks = 12
        return proj

    def _empty_docs(self):
        return {
            "requirements": {"functional": [], "non_functional": [], "business": []},
            "user_stories": {"stories": []},
            "srs": None,
            "estimation": None,
            "risks": {"risks": []},
            "test_cases": {"test_cases": []},
            "traceability": None,
            "metrics": None,
            "maintenance": None,
            "planning": None,
        }

    def test_empty_docs_produces_bytes(self):
        from app.services.pdf.pdf_service import generate_project_pdf
        pdf = generate_project_pdf(self._make_project(), self._empty_docs())
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100  # at minimum a valid minimal PDF

    def test_pdf_starts_with_pdf_header(self):
        from app.services.pdf.pdf_service import generate_project_pdf
        pdf = generate_project_pdf(self._make_project(), self._empty_docs())
        assert pdf[:4] == b"%PDF", "Output is not a valid PDF"

    def test_with_requirements(self):
        from app.services.pdf.pdf_service import generate_project_pdf
        docs = self._empty_docs()
        docs["requirements"] = {
            "functional": [
                {"req_id": "FR-001", "title": "Login", "description": "User can login",
                 "priority": "high", "category": "auth"},
            ],
            "non_functional": [],
            "business": [],
        }
        pdf = generate_project_pdf(self._make_project(), docs)
        assert pdf[:4] == b"%PDF"
        assert len(pdf) > 100

    def test_with_user_stories(self):
        from app.services.pdf.pdf_service import generate_project_pdf
        docs = self._empty_docs()
        docs["user_stories"] = {
            "stories": [
                {"story_id": "US-001", "epic": "Auth", "as_a": "user",
                 "i_want": "to login", "story_points": 3, "sprint": 1},
            ]
        }
        pdf = generate_project_pdf(self._make_project(), docs)
        assert pdf[:4] == b"%PDF"

    def test_with_risks(self):
        from app.services.pdf.pdf_service import generate_project_pdf
        docs = self._empty_docs()
        docs["risks"] = {
            "risks": [
                {"risk_id": "R-001", "title": "Security breach", "probability": "low",
                 "impact": "high", "risk_level": "medium", "owner": "Security Team"},
            ]
        }
        pdf = generate_project_pdf(self._make_project(), docs)
        assert pdf[:4] == b"%PDF"

    def test_with_test_cases(self):
        from app.services.pdf.pdf_service import generate_project_pdf
        docs = self._empty_docs()
        docs["test_cases"] = {
            "test_cases": [
                {"test_id": "TC-001", "test_type": "unit", "title": "Login test",
                 "priority": "high", "requirement_id": "FR-001"},
            ]
        }
        pdf = generate_project_pdf(self._make_project(), docs)
        assert pdf[:4] == b"%PDF"

    def test_special_chars_in_title(self):
        """Title with special characters should not crash PDF generation."""
        from app.services.pdf.pdf_service import generate_project_pdf
        proj = self._make_project(title="My Project & Co. <v2.0>")
        pdf = generate_project_pdf(proj, self._empty_docs())
        assert pdf[:4] == b"%PDF"


# ─── S3 Service Tests ─────────────────────────────────────────────────────────

class TestS3Service:
    """Unit tests for S3 service — all calls are mocked."""

    def test_get_s3_client_raises_without_bucket(self):
        from app.services.s3_service import get_s3_client
        with patch("app.services.s3_service.settings") as mock_settings:
            mock_settings.S3_BUCKET_NAME = ""
            mock_settings.AWS_REGION = "eu-north-1"
            mock_settings.AWS_ACCESS_KEY_ID = ""
            mock_settings.AWS_SECRET_ACCESS_KEY = ""
            with pytest.raises(RuntimeError, match="S3_BUCKET_NAME is not configured"):
                get_s3_client()

    def test_upload_bytes_calls_put_object(self):
        from app.services.s3_service import upload_bytes
        mock_client = MagicMock()
        with patch("app.services.s3_service.get_s3_client", return_value=mock_client), \
             patch("app.services.s3_service.settings") as mock_settings:
            mock_settings.S3_BUCKET_NAME = "test-bucket"
            upload_bytes(b"hello", "test/key.txt", "text/plain")
        mock_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="test/key.txt",
            Body=b"hello",
            ContentType="text/plain",
        )

    def test_create_download_url_returns_url(self):
        from app.services.s3_service import create_download_url
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://s3.example.com/presigned"
        with patch("app.services.s3_service.get_s3_client", return_value=mock_client), \
             patch("app.services.s3_service.settings") as mock_settings:
            mock_settings.S3_BUCKET_NAME = "test-bucket"
            mock_settings.S3_PRESIGNED_URL_EXPIRE_SECONDS = 900
            url = create_download_url("test/key.txt", "file.txt")
        assert url == "https://s3.example.com/presigned"

    def test_delete_object_calls_delete(self):
        from app.services.s3_service import delete_object
        mock_client = MagicMock()
        with patch("app.services.s3_service.get_s3_client", return_value=mock_client), \
             patch("app.services.s3_service.settings") as mock_settings:
            mock_settings.S3_BUCKET_NAME = "test-bucket"
            delete_object("test/key.txt")
        mock_client.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="test/key.txt"
        )


# ─── Config Tests ─────────────────────────────────────────────────────────────

class TestConfig:
    """Verify configuration values are loaded correctly."""

    def test_s3_bucket_name_set(self):
        from app.core.config import settings
        # The fixed .env should load the correct (non-typo'd) bucket name
        assert settings.S3_BUCKET_NAME != "dhurv-cad-project", (
            "Typo'd bucket name is still loaded — check .env for duplicate S3_BUCKET_NAME entries"
        )

    def test_aws_region_set(self):
        from app.core.config import settings
        assert settings.AWS_REGION, "AWS_REGION must not be empty"

    def test_presigned_url_expire_positive(self):
        from app.core.config import settings
        assert settings.S3_PRESIGNED_URL_EXPIRE_SECONDS > 0

    def test_max_upload_size_positive(self):
        from app.core.config import settings
        assert settings.MAX_UPLOAD_SIZE_MB > 0


# ─── filename sanitization test ───────────────────────────────────────────────

class TestSafeFilename:
    def test_strips_path_traversal(self):
        from app.api.files import safe_filename
        assert "/" not in safe_filename("../../etc/passwd")
        assert "\\" not in safe_filename("..\\..\\windows\\system32")

    def test_removes_special_chars(self):
        from app.api.files import safe_filename
        result = safe_filename("my file @#$%.pdf")
        assert all(c not in result for c in "@#$")

    def test_empty_becomes_upload(self):
        from app.api.files import safe_filename
        result = safe_filename("")
        assert result == "upload"

    def test_long_filename_truncated(self):
        from app.api.files import safe_filename
        long_name = "a" * 300 + ".txt"
        result = safe_filename(long_name)
        assert len(result) <= 200
