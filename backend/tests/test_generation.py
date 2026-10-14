"""
Comprehensive tests for all 13 documentation generation features,
S3 persistence, document versioning, and API endpoints.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure backend package is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db, run_migrations
from app.models.user import User
from app.models.project import Project
from app.models.documents import GeneratedDocument, Requirement, UserStory, Diagram, Risk, TestCase, SprintPlan
from app.services.generation_service import GenerationService
from app.services.s3_service import FEATURE_PREFIXES, get_feature_s3_key
from main import app


# ─── Test Database Setup ───────────────────────────────────────────────────────

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    run_migrations(test_engine)
    db = TestingSessionLocal()
    try:
        # Create test user
        user = User(id=1, email="test@example.com", hashed_password="hashedpassword", full_name="Test Engineer")
        db.add(user)
        # Create test project
        project = Project(
            id=1,
            user_id=1,
            title="Cloud Document System",
            description="Enterprise documentation platform with AWS S3 storage",
            domain="web",
            tech_stack=["React", "FastAPI", "Python", "AWS S3", "PostgreSQL"],
            team_size=4,
            timeline_weeks=12,
            objectives="Automate engineering specifications",
            status="draft",
            completion_percentage=0,
            generated_modules=[],
        )
        db.add(project)
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from app.core.deps import get_current_user
    def override_get_current_user():
        return db_session.query(User).filter(User.id == 1).first()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ─── Feature-Specific S3 Prefix Tests ─────────────────────────────────────────

class TestS3Prefixes:
    def test_all_13_features_have_prefixes(self):
        expected_features = [
            "requirements", "user_stories", "srs", "uml", "dfd", "database",
            "planning", "estimation", "risks", "tests", "traceability", "metrics", "maintenance"
        ]
        for feat in expected_features:
            assert feat in FEATURE_PREFIXES, f"Feature {feat} missing from FEATURE_PREFIXES"

    def test_key_structure(self):
        key = get_feature_s3_key(user_id=1, project_id=3, feature="requirements", document_id="doc_123_v1")
        assert key == "users/1/projects/3/requirements/doc_123_v1.json"

        uml_key = get_feature_s3_key(user_id=1, project_id=3, feature="uml", document_id="doc_uml_v1")
        assert uml_key == "users/1/projects/3/uml-diagrams/doc_uml_v1.json"


# ─── Service Unit Tests for All 13 Features ───────────────────────────────────

@pytest.mark.asyncio
class TestGenerationServiceAllFeatures:

    async def test_feature_1_requirements(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_requirements(project)
        assert "functional" in res
        assert "non_functional" in res
        assert "business" in res
        assert len(res["functional"]) > 0
        assert res["version"] == 1
        assert "document_id" in res
        # Verify DB records
        reqs = db_session.query(Requirement).filter(Requirement.project_id == 1).all()
        assert len(reqs) > 0
        # Verify GeneratedDocument
        doc = db_session.query(GeneratedDocument).filter(
            GeneratedDocument.project_id == 1, GeneratedDocument.doc_type == "requirements"
        ).first()
        assert doc is not None
        assert doc.is_latest is True

    async def test_feature_2_user_stories(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_user_stories(project)
        assert "stories" in res
        assert len(res["stories"]) > 0
        assert res["total_story_points"] > 0
        stories = db_session.query(UserStory).filter(UserStory.project_id == 1).all()
        assert len(stories) == len(res["stories"])

    async def test_feature_3_srs(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_srs(project)
        assert "document_info" in res
        assert "section_1_introduction" in res
        assert "section_2_overall_description" in res

    async def test_feature_4_uml_diagrams(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_diagrams(project, "uml")
        assert "diagrams" in res
        assert len(res["diagrams"]) > 0
        diag_types = [d["diagram_type"] for d in res["diagrams"]]
        assert "use_case" in diag_types
        assert "class" in diag_types
        db_diags = db_session.query(Diagram).filter(Diagram.project_id == 1, Diagram.category == "uml").all()
        assert len(db_diags) > 0

    async def test_feature_5_dfd_diagrams(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_diagrams(project, "dfd")
        assert "diagrams" in res
        assert len(res["diagrams"]) > 0
        diag_types = [d["diagram_type"] for d in res["diagrams"]]
        assert "context_diagram" in diag_types or "dfd_level0" in diag_types

    async def test_feature_6_database_design(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_database_design(project)
        assert "entities" in res
        assert "relationships" in res
        assert "sql_schema" in res
        assert len(res["entities"]) >= 3

    async def test_feature_7_project_planning(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_planning(project)
        assert "sprints" in res
        assert "gantt_data" in res
        assert "pert_data" in res
        assert len(res["sprints"]) > 0

    async def test_feature_8_estimation(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_estimation(project)
        assert "cocomo" in res
        assert "function_point" in res
        assert "time_estimation" in res
        assert "cost_estimation" in res
        assert res["cocomo"]["effort_person_months"] > 0

    async def test_feature_9_risk_management(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_risks(project)
        assert "risks" in res
        assert len(res["risks"]) > 0
        db_risks = db_session.query(Risk).filter(Risk.project_id == 1).all()
        assert len(db_risks) == len(res["risks"])

    async def test_feature_10_test_cases(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_test_cases(project)
        assert "test_cases" in res
        assert len(res["test_cases"]) > 0
        db_cases = db_session.query(TestCase).filter(TestCase.project_id == 1).all()
        assert len(db_cases) == len(res["test_cases"])

    async def test_feature_11_traceability(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_traceability(project)
        assert "matrix" in res
        assert "coverage_percentage" in res
        assert len(res["matrix"]) > 0

    async def test_feature_12_quality_metrics(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_metrics(project)
        assert "metrics" in res
        assert "cyclomatic_complexity" in res["metrics"]
        assert "maintainability_index" in res["metrics"]

    async def test_feature_13_maintenance(self, db_session):
        project = db_session.query(Project).filter(Project.id == 1).first()
        svc = GenerationService(db_session)
        res = await svc.generate_maintenance(project)
        assert "corrective_maintenance" in res
        assert "preventive_maintenance" in res
        assert "adaptive_maintenance" in res


# ─── API Endpoints Tests for All 13 Features ─────────────────────────────────

class TestApiEndpointsAllFeatures:

    def test_generate_and_get_all_13_endpoints(self, client):
        endpoints = [
            ("requirements/generate", "requirements"),
            ("user-stories/generate", "user-stories"),
            ("srs/generate", "srs"),
            ("diagrams/uml/generate", "diagrams?category=uml"),
            ("diagrams/dfd/generate", "diagrams?category=dfd"),
            ("database/generate", "database"),
            ("planning/generate", "planning"),
            ("estimation/generate", "estimation"),
            ("risks/generate", "risks"),
            ("tests/generate", "tests"),
            ("traceability/generate", "traceability"),
            ("metrics/generate", "metrics"),
            ("maintenance/generate", "maintenance"),
        ]

        for gen_path, get_path in endpoints:
            # 1. POST generate
            res_post = client.post(f"/api/projects/1/{gen_path}")
            assert res_post.status_code == 200, f"POST /api/projects/1/{gen_path} failed with {res_post.status_code}: {res_post.text}"

            # 2. GET retrieve
            res_get = client.get(f"/api/projects/1/{get_path}")
            assert res_get.status_code == 200, f"GET /api/projects/1/{get_path} failed with {res_get.status_code}: {res_get.text}"

    def test_nonexistent_project_returns_404(self, client):
        res = client.post("/api/projects/9999/requirements/generate")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    def test_versioning_and_regeneration(self, client, db_session):
        # Generate twice to verify version increment
        res1 = client.post("/api/projects/1/requirements/generate")
        assert res1.status_code == 200
        assert res1.json()["version"] == 1

        res2 = client.post("/api/projects/1/requirements/generate")
        assert res2.status_code == 200
        assert res2.json()["version"] == 2

        # Check in database: v1 is is_latest=False, v2 is is_latest=True
        docs = db_session.query(GeneratedDocument).filter(
            GeneratedDocument.project_id == 1,
            GeneratedDocument.doc_type == "requirements"
        ).order_by(GeneratedDocument.version.asc()).all()

        assert len(docs) == 2
        assert docs[0].version == 1 and docs[0].is_latest is False
        assert docs[1].version == 2 and docs[1].is_latest is True

    def test_document_management_endpoints(self, client):
        # 1. Generate requirements
        client.post("/api/projects/1/requirements/generate")

        # 2. List documents
        res_list = client.get("/api/projects/1/documents")
        assert res_list.status_code == 200
        docs = res_list.json()["documents"]
        assert len(docs) >= 1
        doc_id = docs[0]["document_id"]
        assert doc_id is not None

        # 3. Get document by ID
        res_get = client.get(f"/api/projects/1/documents/{doc_id}")
        assert res_get.status_code == 200
        assert res_get.json()["document_id"] == doc_id

        # 4. Update document
        res_put = client.put(f"/api/projects/1/documents/{doc_id}", json={"content": {"updated": True}})
        assert res_put.status_code == 200
        assert res_put.json()["version"] == 2
