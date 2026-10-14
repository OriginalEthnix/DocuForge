"""
Generation Service — Orchestrates AI generation, S3 persistence, versioning,
and database synchronization for all 13 documentation modules.
"""
from datetime import datetime
import re
from typing import Any, Dict, Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from loguru import logger

from app.models.project import Project
from app.models.documents import (
    Requirement, UserStory, Diagram, Risk, TestCase, SprintPlan, GeneratedDocument
)
from app.services.ai.gemini_service import get_ai_provider
from app.services.ai.prompt_builder import (
    build_requirements_prompt, build_user_stories_prompt, build_srs_prompt,
    build_uml_prompt, build_dfd_prompt, build_database_prompt,
    build_planning_prompt, build_estimation_prompt, build_risk_prompt,
    build_test_cases_prompt, build_traceability_prompt,
    build_metrics_prompt, build_maintenance_prompt,
)
from app.services.ai.fallback_generator import (
    generate_fallback_requirements, generate_fallback_user_stories,
    generate_fallback_srs, generate_fallback_uml, generate_fallback_dfd,
    generate_fallback_database, generate_fallback_planning,
    generate_fallback_estimation, generate_fallback_risks,
    generate_fallback_test_cases, generate_fallback_traceability,
    generate_fallback_metrics, generate_fallback_maintenance,
)
from app.services.s3_service import (
    upload_json, delete_object, create_download_url,
    get_feature_s3_key, FEATURE_PREFIXES, is_s3_error
)
from app.services.diagram.plantuml_service import render_plantuml_to_svg


class GenerationService:
    """Orchestrates all AI documentation generation workflows with S3 storage and versioning."""

    def __init__(self, db: Session):
        self.db = db
        self.ai = get_ai_provider()

    def _update_project_progress(self, project: Project, module: str):
        """Track which modules have been generated and calculate progress."""
        modules = list(project.generated_modules or [])
        if module not in modules:
            modules.append(module)
        project.generated_modules = modules
        project.completion_percentage = min(100, int((len(modules) / 13) * 100))
        if project.completion_percentage > 0:
            project.status = "in_progress"
        if project.completion_percentage >= 100:
            project.status = "completed"
        self.db.commit()

    def _persist_and_upload(
        self,
        project: Project,
        doc_type: str,
        content: Dict[str, Any],
        feature_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Saves document to S3 feature-specific prefix, creates a versioned GeneratedDocument
        record, manages previous version flags, and generates a presigned download URL.
        """
        feat = feature_key or doc_type
        # Find previous latest version
        existing = self.db.query(GeneratedDocument).filter(
            GeneratedDocument.project_id == project.id,
            GeneratedDocument.doc_type == doc_type,
            GeneratedDocument.is_latest == True,
        ).first()

        version = (existing.version + 1) if existing else 1
        doc_id = f"doc_{uuid4().hex[:12]}"
        s3_key = get_feature_s3_key(
            user_id=project.user_id,
            project_id=project.id,
            feature=feat,
            document_id=f"{doc_id}_v{version}"
        )

        # Upload JSON artifact to AWS S3
        payload_bytes = b""
        s3_uploaded = False
        try:
            payload_bytes = upload_json(content, s3_key)
            s3_uploaded = True
            logger.info(f"Artifact uploaded to S3: {s3_key} ({len(payload_bytes)} bytes)")
        except Exception as s3_err:
            logger.warning(f"Could not upload artifact to S3 ({s3_key}): {s3_err}")
            # If S3 is unconfigured or fails, continue with metadata persistence
            # so the application remains functional even in offline/test environments

        # Generate download URL if uploaded
        download_url = None
        if s3_uploaded:
            try:
                safe_title = re.sub(r"[^A-Za-z0-9_-]", "_", project.title).strip("_")
                download_filename = f"{safe_title}_{feat}_v{version}.json"
                download_url = create_download_url(s3_key, download_filename)
            except Exception as url_err:
                logger.warning(f"Failed to generate presigned download URL for {s3_key}: {url_err}")

        # Update previous version to is_latest=False
        try:
            if existing:
                existing.is_latest = False

            doc_record = GeneratedDocument(
                document_id=doc_id,
                project_id=project.id,
                doc_type=doc_type,
                content=content,
                s3_key=s3_key if s3_uploaded else None,
                content_type="application/json",
                file_size_bytes=len(payload_bytes) if payload_bytes else None,
                version=version,
                status="completed",
                is_latest=True,
                meta={"feature_key": feat, "s3_uploaded": s3_uploaded}
            )
            self.db.add(doc_record)
            self.db.commit()
            self.db.refresh(doc_record)
        except Exception as db_err:
            self.db.rollback()
            if s3_uploaded:
                try:
                    delete_object(s3_key)
                    logger.info(f"Cleaned up orphaned S3 object after DB rollback: {s3_key}")
                except Exception:
                    pass
            logger.error(f"Failed to persist GeneratedDocument to DB: {db_err}")
            raise db_err

        content["document_id"] = doc_id
        content["version"] = version
        content["s3_key"] = s3_key if s3_uploaded else None
        content["download_url"] = download_url
        content["status"] = "completed"
        content["project_id"] = project.id
        content["generated_at"] = datetime.utcnow().isoformat()
        return content

    # ─── 1. Requirements ──────────────────────────────────────────────────────────

    async def generate_requirements(self, project: Project) -> Dict[str, Any]:
        """Generate IEEE 830 functional, non-functional, and business requirements."""
        logger.info(f"Generating requirements for project {project.id}")
        data = None
        try:
            prompt = build_requirements_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or ("functional" not in data and "non_functional" not in data):
                logger.warning("AI output missing requirements structure; using fallback")
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for requirements: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_requirements(project)

        # Clear existing relational requirements
        self.db.query(Requirement).filter(Requirement.project_id == project.id).delete()

        # Save functional requirements
        for req in data.get("functional", []):
            self.db.add(Requirement(
                project_id=project.id,
                req_type="functional",
                req_id=req.get("req_id"),
                title=req.get("title", "Functional Requirement"),
                description=req.get("description", ""),
                priority=req.get("priority", "medium").lower(),
                category=req.get("category", "General"),
                acceptance_criteria=req.get("acceptance_criteria"),
            ))

        # Save non-functional requirements
        for req in data.get("non_functional", []):
            self.db.add(Requirement(
                project_id=project.id,
                req_type="non_functional",
                req_id=req.get("req_id"),
                title=req.get("title", "Non-Functional Requirement"),
                description=req.get("description", ""),
                priority=req.get("priority", "medium").lower(),
                category=req.get("category", "Quality Attribute"),
                acceptance_criteria=req.get("acceptance_criteria"),
            ))

        # Save business requirements
        for req in data.get("business", []):
            self.db.add(Requirement(
                project_id=project.id,
                req_type="business",
                req_id=req.get("req_id"),
                title=req.get("title", "Business Requirement"),
                description=req.get("description", ""),
                priority=req.get("priority", "medium").lower(),
                category=req.get("category", "Business"),
                acceptance_criteria=req.get("acceptance_criteria"),
            ))

        self.db.commit()

        # Upload artifact to S3 and save versioned metadata
        result = self._persist_and_upload(project, "requirements", data, "requirements")
        self._update_project_progress(project, "requirements")
        return result

    # ─── 2. User Stories ─────────────────────────────────────────────────────────

    async def generate_user_stories(self, project: Project) -> Dict[str, Any]:
        """Generate Agile user stories with acceptance criteria, story points, and sprints."""
        logger.info(f"Generating user stories for project {project.id}")
        data = None
        try:
            prompt = build_user_stories_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "stories" not in data or not data["stories"]:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for user stories: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_user_stories(project)

        self.db.query(UserStory).filter(UserStory.project_id == project.id).delete()

        total_points = 0
        for story in data.get("stories", []):
            pts = story.get("story_points", 3)
            total_points += pts
            self.db.add(UserStory(
                project_id=project.id,
                story_id=story.get("story_id"),
                epic=story.get("epic", "General"),
                title=story.get("title", "User Story"),
                as_a=story.get("as_a", "user"),
                i_want=story.get("i_want", ""),
                so_that=story.get("so_that", ""),
                acceptance_criteria=story.get("acceptance_criteria", []),
                story_points=pts,
                priority=story.get("priority", "medium").lower(),
                sprint=story.get("sprint", 1),
            ))

        data["total_story_points"] = total_points
        self.db.commit()

        result = self._persist_and_upload(project, "user_stories", data, "user_stories")
        self._update_project_progress(project, "user_stories")
        return result

    # ─── 3. SRS Document ─────────────────────────────────────────────────────────

    async def generate_srs(self, project: Project) -> Dict[str, Any]:
        """Generate IEEE 830 Software Requirements Specification."""
        logger.info(f"Generating SRS for project {project.id}")
        data = None
        try:
            prompt = build_srs_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "section_1_introduction" not in data:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for SRS: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_srs(project)

        result = self._persist_and_upload(project, "srs", data, "srs")
        self._update_project_progress(project, "srs")
        return result

    # ─── 4 & 5. Diagrams (UML & DFD) ─────────────────────────────────────────────

    async def generate_diagrams(self, project: Project, diagram_type: str = "uml") -> Dict[str, Any]:
        """Generate UML or DFD diagrams with PlantUML code and SVG rendering."""
        logger.info(f"Generating {diagram_type} diagrams for project {project.id}")
        data = None
        try:
            if diagram_type == "uml":
                prompt = build_uml_prompt(project)
            else:
                prompt = build_dfd_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "diagrams" not in data or not data["diagrams"]:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for {diagram_type} diagrams: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_uml(project) if diagram_type == "uml" else generate_fallback_dfd(project)

        # Clear existing diagrams of this category
        self.db.query(Diagram).filter(
            Diagram.project_id == project.id,
            Diagram.category == diagram_type
        ).delete()

        result_diagrams = []
        for diag in data.get("diagrams", []):
            plantuml_code = diag.get("plantuml_code", "")
            svg = None
            if plantuml_code:
                try:
                    svg = await render_plantuml_to_svg(plantuml_code)
                except Exception as ren_err:
                    logger.warning(f"PlantUML rendering failed: {ren_err}")

            db_diag = Diagram(
                project_id=project.id,
                diagram_type=diag.get("diagram_type", "diagram"),
                title=diag.get("title", f"{diagram_type.upper()} Diagram"),
                plantuml_code=plantuml_code,
                svg_content=svg,
                category=diag.get("category", diagram_type),
            )
            self.db.add(db_diag)
            self.db.flush()

            result_diagrams.append({
                "id": db_diag.id,
                "diagram_type": db_diag.diagram_type,
                "title": db_diag.title,
                "plantuml_code": plantuml_code,
                "svg_content": svg,
                "category": db_diag.category,
            })

        self.db.commit()

        doc_payload = {
            "project_id": project.id,
            "diagrams": result_diagrams,
            "category": diagram_type,
        }

        feature_key = "uml" if diagram_type == "uml" else "dfd"
        result = self._persist_and_upload(project, f"{diagram_type}_diagrams", doc_payload, feature_key)
        module_name = "uml_diagrams" if diagram_type == "uml" else "dfd_diagrams"
        self._update_project_progress(project, module_name)
        return result

    # ─── 6. Database Design ──────────────────────────────────────────────────────

    async def generate_database_design(self, project: Project) -> Dict[str, Any]:
        """Generate normalized database tables, relationships, ER diagram, and SQL schema."""
        logger.info(f"Generating database design for project {project.id}")
        data = None
        try:
            prompt = build_database_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "entities" not in data:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for database design: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_database(project)

        # Render ER diagram if PlantUML provided
        er_code = data.get("er_diagram_plantuml", "")
        if er_code:
            try:
                svg = await render_plantuml_to_svg(er_code)
                if svg:
                    data["er_diagram_svg"] = svg
            except Exception:
                pass

        result = self._persist_and_upload(project, "database_design", data, "database")
        self._update_project_progress(project, "database_design")
        return result

    # ─── 7. Project Planning ─────────────────────────────────────────────────────

    async def generate_planning(self, project: Project) -> Dict[str, Any]:
        """Generate Agile sprints, Gantt timeline, PERT analysis, and release plan."""
        logger.info(f"Generating planning for project {project.id}")
        data = None
        try:
            prompt = build_planning_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "sprints" not in data:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for planning: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_planning(project)

        # Save sprint plans to relational table
        self.db.query(SprintPlan).filter(SprintPlan.project_id == project.id).delete()
        for sprint in data.get("sprints", []):
            self.db.add(SprintPlan(
                project_id=project.id,
                sprint_number=sprint.get("sprint_number", 1),
                sprint_goal=sprint.get("sprint_goal", ""),
                duration_weeks=sprint.get("duration_weeks", 2),
                stories=sprint.get("stories", []),
                milestones=sprint.get("milestones", []),
            ))

        self.db.commit()

        result = self._persist_and_upload(project, "planning", data, "planning")
        self._update_project_progress(project, "planning")
        return result

    # ─── 8. Estimation ───────────────────────────────────────────────────────────

    async def generate_estimation(self, project: Project) -> Dict[str, Any]:
        """Generate COCOMO, Function Point Analysis, PERT duration, cost, and team sizing."""
        logger.info(f"Generating estimation for project {project.id}")
        data = None
        try:
            prompt = build_estimation_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "cocomo" not in data:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for estimation: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_estimation(project)

        result = self._persist_and_upload(project, "estimation", data, "estimation")
        self._update_project_progress(project, "estimation")
        return result

    # ─── 9. Risk Management ──────────────────────────────────────────────────────

    async def generate_risks(self, project: Project) -> Dict[str, Any]:
        """Generate Risk Register with probability, impact, scoring, and mitigation plans."""
        logger.info(f"Generating risk register for project {project.id}")
        data = None
        try:
            prompt = build_risk_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "risks" not in data or not data["risks"]:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for risks: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_risks(project)

        self.db.query(Risk).filter(Risk.project_id == project.id).delete()
        for r in data.get("risks", []):
            self.db.add(Risk(
                project_id=project.id,
                risk_id=r.get("risk_id"),
                title=r.get("title", "Project Risk"),
                description=r.get("description", ""),
                category=r.get("category", "General"),
                probability=r.get("probability", "medium").lower(),
                impact=r.get("impact", "medium").lower(),
                risk_level=r.get("risk_level", "medium").lower(),
                mitigation_strategy=r.get("mitigation_strategy", "Monitor closely"),
                contingency_plan=r.get("contingency_plan", "Escalate to lead"),
                owner=r.get("owner", "Team"),
                status=r.get("status", "open").lower(),
            ))

        self.db.commit()

        result = self._persist_and_upload(project, "risks", data, "risks")
        self._update_project_progress(project, "risks")
        return result

    # ─── 10. Test Cases ──────────────────────────────────────────────────────────

    async def generate_test_cases(self, project: Project) -> Dict[str, Any]:
        """Generate test cases across unit, integration, system, acceptance, and boundary."""
        logger.info(f"Generating test cases for project {project.id}")
        data = None
        try:
            prompt = build_test_cases_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "test_cases" not in data or not data["test_cases"]:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for test cases: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_test_cases(project)

        self.db.query(TestCase).filter(TestCase.project_id == project.id).delete()
        for tc in data.get("test_cases", []):
            self.db.add(TestCase(
                project_id=project.id,
                test_id=tc.get("test_id"),
                test_type=tc.get("test_type", "unit").lower(),
                title=tc.get("title", "Test Case"),
                description=tc.get("description", ""),
                preconditions=tc.get("preconditions"),
                test_steps=tc.get("test_steps", []),
                expected_result=tc.get("expected_result", "Pass"),
                priority=tc.get("priority", "medium").lower(),
                status="not_executed",
                requirement_id=tc.get("requirement_id"),
            ))

        self.db.commit()

        result = self._persist_and_upload(project, "test_cases", data, "tests")
        self._update_project_progress(project, "test_cases")
        return result

    # ─── 11. Traceability ────────────────────────────────────────────────────────

    async def generate_traceability(self, project: Project) -> Dict[str, Any]:
        """Generate Requirements Traceability Matrix linking requirements to design and tests."""
        logger.info(f"Generating traceability matrix for project {project.id}")
        data = None
        try:
            prompt = build_traceability_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "matrix" not in data:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for traceability: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_traceability(project)

        result = self._persist_and_upload(project, "traceability", data, "traceability")
        self._update_project_progress(project, "traceability")
        return result

    # ─── 12. Quality Metrics ─────────────────────────────────────────────────────

    async def generate_metrics(self, project: Project) -> Dict[str, Any]:
        """Generate quality metrics dashboard (complexity, coverage, maintainability, debt)."""
        logger.info(f"Generating quality metrics for project {project.id}")
        data = None
        try:
            prompt = build_metrics_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "metrics" not in data:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for metrics: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_metrics(project)

        result = self._persist_and_upload(project, "metrics", data, "metrics")
        self._update_project_progress(project, "metrics")
        return result

    # ─── 13. Maintenance ─────────────────────────────────────────────────────────

    async def generate_maintenance(self, project: Project) -> Dict[str, Any]:
        """Generate software maintenance plan (corrective, adaptive, preventive, perfective)."""
        logger.info(f"Generating maintenance plan for project {project.id}")
        data = None
        try:
            prompt = build_maintenance_prompt(project)
            data = await self.ai.generate_json(prompt)
            if not isinstance(data, dict) or "overview" not in data:
                data = None
        except Exception as e:
            logger.warning(f"AI generation failed for maintenance: {e}. Using deterministic generator.")
            data = None

        if not data:
            data = generate_fallback_maintenance(project)

        result = self._persist_and_upload(project, "maintenance", data, "maintenance")
        self._update_project_progress(project, "maintenance")
        return result
