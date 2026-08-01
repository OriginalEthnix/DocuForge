"""
Generation Service — Orchestrates AI generation for all 13 documentation modules.
"""
from datetime import datetime
from typing import Any, Dict, Optional
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
from app.services.diagram.plantuml_service import render_plantuml_to_svg


class GenerationService:
    """Orchestrates all AI documentation generation workflows."""

    def __init__(self, db: Session):
        self.db = db
        self.ai = get_ai_provider()

    def _update_project_progress(self, project: Project, module: str):
        """Track which modules have been generated."""
        modules = list(project.generated_modules or [])
        if module not in modules:
            modules.append(module)
        project.generated_modules = modules
        # Calculate completion percentage (13 modules total)
        project.completion_percentage = min(100, int((len(modules) / 13) * 100))
        if project.completion_percentage > 0:
            project.status = "in_progress"
        if project.completion_percentage >= 100:
            project.status = "completed"
        self.db.commit()

    async def generate_requirements(self, project: Project) -> Dict[str, Any]:
        """Generate requirements analysis."""
        logger.info(f"Generating requirements for project {project.id}")
        prompt = build_requirements_prompt(project)
        data = await self.ai.generate_json(prompt)

        # Clear existing requirements
        self.db.query(Requirement).filter(Requirement.project_id == project.id).delete()

        # Save functional requirements
        for req in data.get("functional", []):
            self.db.add(Requirement(
                project_id=project.id,
                req_type="functional",
                req_id=req.get("req_id"),
                title=req.get("title"),
                description=req.get("description"),
                priority=req.get("priority", "medium"),
                category=req.get("category"),
                acceptance_criteria=req.get("acceptance_criteria"),
            ))

        # Save non-functional requirements
        for req in data.get("non_functional", []):
            self.db.add(Requirement(
                project_id=project.id,
                req_type="non_functional",
                req_id=req.get("req_id"),
                title=req.get("title"),
                description=req.get("description"),
                priority=req.get("priority", "medium"),
                category=req.get("category"),
                acceptance_criteria=req.get("acceptance_criteria"),
            ))

        # Save business requirements
        for req in data.get("business", []):
            self.db.add(Requirement(
                project_id=project.id,
                req_type="business",
                req_id=req.get("req_id"),
                title=req.get("title"),
                description=req.get("description"),
                priority=req.get("priority", "medium"),
                category=req.get("category"),
            ))

        self.db.commit()
        self._update_project_progress(project, "requirements")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_user_stories(self, project: Project) -> Dict[str, Any]:
        """Generate Agile user stories."""
        logger.info(f"Generating user stories for project {project.id}")
        prompt = build_user_stories_prompt(project)
        data = await self.ai.generate_json(prompt)

        self.db.query(UserStory).filter(UserStory.project_id == project.id).delete()

        total_points = 0
        for story in data.get("stories", []):
            pts = story.get("story_points", 1)
            total_points += pts
            self.db.add(UserStory(
                project_id=project.id,
                story_id=story.get("story_id"),
                epic=story.get("epic"),
                title=story.get("title"),
                as_a=story.get("as_a"),
                i_want=story.get("i_want"),
                so_that=story.get("so_that"),
                acceptance_criteria=story.get("acceptance_criteria", []),
                story_points=pts,
                priority=story.get("priority", "medium"),
                sprint=story.get("sprint", 1),
            ))

        data["total_story_points"] = total_points
        self.db.commit()
        self._update_project_progress(project, "user_stories")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_srs(self, project: Project) -> Dict[str, Any]:
        """Generate IEEE SRS document."""
        logger.info(f"Generating SRS for project {project.id}")
        prompt = build_srs_prompt(project)
        data = await self.ai.generate_json(prompt)

        # Save as generated document
        self._save_document(project.id, "srs", data)
        self._update_project_progress(project, "srs")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_diagrams(self, project: Project, diagram_type: str = "uml") -> Dict[str, Any]:
        """Generate UML or DFD diagrams."""
        logger.info(f"Generating {diagram_type} diagrams for project {project.id}")

        if diagram_type == "uml":
            prompt = build_uml_prompt(project)
        else:
            prompt = build_dfd_prompt(project)

        data = await self.ai.generate_json(prompt)

        # Remove existing diagrams of this category
        self.db.query(Diagram).filter(
            Diagram.project_id == project.id,
            Diagram.category == diagram_type
        ).delete()

        result_diagrams = []
        for diag in data.get("diagrams", []):
            plantuml_code = diag.get("plantuml_code", "")
            # Try to render SVG
            svg = await render_plantuml_to_svg(plantuml_code)

            db_diag = Diagram(
                project_id=project.id,
                diagram_type=diag.get("diagram_type"),
                title=diag.get("title"),
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
        module_name = "uml_diagrams" if diagram_type == "uml" else "dfd_diagrams"
        self._update_project_progress(project, module_name)
        return {
            "project_id": project.id,
            "diagrams": result_diagrams,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def generate_database_design(self, project: Project) -> Dict[str, Any]:
        """Generate database design with ER diagram."""
        logger.info(f"Generating database design for project {project.id}")
        prompt = build_database_prompt(project)
        data = await self.ai.generate_json(prompt)

        # Render ER diagram
        er_code = data.get("er_diagram_plantuml", "")
        if er_code:
            svg = await render_plantuml_to_svg(er_code)
            if svg:
                data["er_diagram_svg"] = svg

        self._save_document(project.id, "database_design", data)
        self._update_project_progress(project, "database_design")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_planning(self, project: Project) -> Dict[str, Any]:
        """Generate project planning including sprints, Gantt, and PERT."""
        logger.info(f"Generating planning for project {project.id}")
        prompt = build_planning_prompt(project)
        data = await self.ai.generate_json(prompt)

        # Save sprint plans
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
        self._save_document(project.id, "planning", data)
        self._update_project_progress(project, "planning")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_estimation(self, project: Project) -> Dict[str, Any]:
        """Generate COCOMO, FPA, and cost estimation."""
        logger.info(f"Generating estimation for project {project.id}")
        prompt = build_estimation_prompt(project)
        data = await self.ai.generate_json(prompt)
        self._save_document(project.id, "estimation", data)
        self._update_project_progress(project, "estimation")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_risks(self, project: Project) -> Dict[str, Any]:
        """Generate risk register."""
        logger.info(f"Generating risk register for project {project.id}")
        prompt = build_risk_prompt(project)
        data = await self.ai.generate_json(prompt)

        self.db.query(Risk).filter(Risk.project_id == project.id).delete()
        for risk in data.get("risks", []):
            self.db.add(Risk(
                project_id=project.id,
                risk_id=risk.get("risk_id"),
                title=risk.get("title"),
                description=risk.get("description"),
                category=risk.get("category"),
                probability=risk.get("probability", "medium"),
                impact=risk.get("impact", "medium"),
                risk_level=risk.get("risk_level", "medium"),
                mitigation_strategy=risk.get("mitigation_strategy"),
                contingency_plan=risk.get("contingency_plan"),
                owner=risk.get("owner"),
                status=risk.get("status", "open"),
            ))

        self.db.commit()
        self._update_project_progress(project, "risks")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_test_cases(self, project: Project) -> Dict[str, Any]:
        """Generate comprehensive test cases."""
        logger.info(f"Generating test cases for project {project.id}")
        prompt = build_test_cases_prompt(project)
        data = await self.ai.generate_json(prompt)

        self.db.query(TestCase).filter(TestCase.project_id == project.id).delete()
        for tc in data.get("test_cases", []):
            self.db.add(TestCase(
                project_id=project.id,
                test_id=tc.get("test_id"),
                test_type=tc.get("test_type"),
                title=tc.get("title"),
                description=tc.get("description"),
                preconditions=tc.get("preconditions"),
                test_steps=tc.get("test_steps", []),
                expected_result=tc.get("expected_result"),
                priority=tc.get("priority", "medium"),
                requirement_id=tc.get("requirement_id"),
            ))

        self.db.commit()
        self._update_project_progress(project, "test_cases")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_traceability(self, project: Project) -> Dict[str, Any]:
        """Generate Requirements Traceability Matrix."""
        logger.info(f"Generating traceability matrix for project {project.id}")
        prompt = build_traceability_prompt(project)
        data = await self.ai.generate_json(prompt)
        self._save_document(project.id, "traceability", data)
        self._update_project_progress(project, "traceability")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_metrics(self, project: Project) -> Dict[str, Any]:
        """Generate quality metrics."""
        logger.info(f"Generating quality metrics for project {project.id}")
        prompt = build_metrics_prompt(project)
        data = await self.ai.generate_json(prompt)
        self._save_document(project.id, "metrics", data)
        self._update_project_progress(project, "metrics")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    async def generate_maintenance(self, project: Project) -> Dict[str, Any]:
        """Generate maintenance plan."""
        logger.info(f"Generating maintenance plan for project {project.id}")
        prompt = build_maintenance_prompt(project)
        data = await self.ai.generate_json(prompt)
        self._save_document(project.id, "maintenance", data)
        self._update_project_progress(project, "maintenance")
        data["generated_at"] = datetime.utcnow().isoformat()
        data["project_id"] = project.id
        return data

    def _save_document(self, project_id: int, doc_type: str, content: Dict[str, Any]):
        """Save or update a generated document."""
        existing = self.db.query(GeneratedDocument).filter(
            GeneratedDocument.project_id == project_id,
            GeneratedDocument.doc_type == doc_type,
            GeneratedDocument.is_latest == True,
        ).first()

        if existing:
            existing.is_latest = False

        version = (existing.version + 1) if existing else 1
        self.db.add(GeneratedDocument(
            project_id=project_id,
            doc_type=doc_type,
            content=content,
            version=version,
            is_latest=True,
        ))
        self.db.commit()
