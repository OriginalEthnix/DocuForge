"""
AI Generation API Router — All 13 generation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.documents import Requirement, UserStory, Diagram, Risk, TestCase, GeneratedDocument
from app.services.generation_service import GenerationService

router = APIRouter()


def _get_project_or_404(project_id: int, user: User, db: Session) -> Project:
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


# ─── Requirements ────────────────────────────────────────────────────────────

@router.post("/{project_id}/requirements/generate")
async def generate_requirements(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_requirements(project)


@router.get("/{project_id}/requirements")
def get_requirements(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

    result = {"functional": [], "non_functional": [], "business": [], "project_id": project_id}
    for req in requirements:
        item = {
            "id": req.id, "req_id": req.req_id, "title": req.title,
            "description": req.description, "priority": req.priority,
            "category": req.category, "acceptance_criteria": req.acceptance_criteria,
        }
        key = req.req_type if req.req_type in result else "functional"
        result[key].append(item)
    return result


# ─── User Stories ────────────────────────────────────────────────────────────

@router.post("/{project_id}/user-stories/generate")
async def generate_user_stories(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_user_stories(project)


@router.get("/{project_id}/user-stories")
def get_user_stories(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    stories = db.query(UserStory).filter(UserStory.project_id == project_id).all()
    return {
        "project_id": project_id,
        "stories": [
            {
                "id": s.id, "story_id": s.story_id, "epic": s.epic, "title": s.title,
                "as_a": s.as_a, "i_want": s.i_want, "so_that": s.so_that,
                "acceptance_criteria": s.acceptance_criteria, "story_points": s.story_points,
                "priority": s.priority, "sprint": s.sprint, "status": s.status,
            }
            for s in stories
        ],
        "total_story_points": sum(s.story_points for s in stories),
    }


# ─── SRS ─────────────────────────────────────────────────────────────────────

@router.post("/{project_id}/srs/generate")
async def generate_srs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_srs(project)


@router.get("/{project_id}/srs")
def get_srs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "srs")


# ─── UML Diagrams ────────────────────────────────────────────────────────────

@router.post("/{project_id}/diagrams/uml/generate")
async def generate_uml(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_diagrams(project, "uml")


@router.post("/{project_id}/diagrams/dfd/generate")
async def generate_dfd(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_diagrams(project, "dfd")


@router.get("/{project_id}/diagrams")
def get_diagrams(
    project_id: int,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    query = db.query(Diagram).filter(Diagram.project_id == project_id)
    if category:
        query = query.filter(Diagram.category == category)
    diagrams = query.all()
    return {
        "project_id": project_id,
        "diagrams": [
            {
                "id": d.id, "diagram_type": d.diagram_type, "title": d.title,
                "plantuml_code": d.plantuml_code, "svg_content": d.svg_content,
                "category": d.category,
            }
            for d in diagrams
        ],
    }


# ─── Database Design ─────────────────────────────────────────────────────────

@router.post("/{project_id}/database/generate")
async def generate_database(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_database_design(project)


@router.get("/{project_id}/database")
def get_database(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "database_design")


# ─── Planning ────────────────────────────────────────────────────────────────

@router.post("/{project_id}/planning/generate")
async def generate_planning(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_planning(project)


@router.get("/{project_id}/planning")
def get_planning(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "planning")


# ─── Estimation ──────────────────────────────────────────────────────────────

@router.post("/{project_id}/estimation/generate")
async def generate_estimation(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_estimation(project)


@router.get("/{project_id}/estimation")
def get_estimation(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "estimation")


# ─── Risks ───────────────────────────────────────────────────────────────────

@router.post("/{project_id}/risks/generate")
async def generate_risks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_risks(project)


@router.get("/{project_id}/risks")
def get_risks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    risks = db.query(Risk).filter(Risk.project_id == project_id).all()
    return {
        "project_id": project_id,
        "risks": [
            {
                "id": r.id, "risk_id": r.risk_id, "title": r.title,
                "description": r.description, "category": r.category,
                "probability": r.probability, "impact": r.impact,
                "risk_level": r.risk_level, "mitigation_strategy": r.mitigation_strategy,
                "contingency_plan": r.contingency_plan, "owner": r.owner, "status": r.status,
            }
            for r in risks
        ],
    }


# ─── Test Cases ──────────────────────────────────────────────────────────────

@router.post("/{project_id}/tests/generate")
async def generate_tests(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_test_cases(project)


@router.get("/{project_id}/tests")
def get_tests(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    cases = db.query(TestCase).filter(TestCase.project_id == project_id).all()
    return {
        "project_id": project_id,
        "test_cases": [
            {
                "id": t.id, "test_id": t.test_id, "test_type": t.test_type,
                "title": t.title, "description": t.description,
                "preconditions": t.preconditions, "test_steps": t.test_steps,
                "expected_result": t.expected_result, "priority": t.priority,
                "status": t.status, "requirement_id": t.requirement_id,
            }
            for t in cases
        ],
    }


# ─── Traceability ────────────────────────────────────────────────────────────

@router.post("/{project_id}/traceability/generate")
async def generate_traceability(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_traceability(project)


@router.get("/{project_id}/traceability")
def get_traceability(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "traceability")


# ─── Metrics ─────────────────────────────────────────────────────────────────

@router.post("/{project_id}/metrics/generate")
async def generate_metrics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_metrics(project)


@router.get("/{project_id}/metrics")
def get_metrics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "metrics")


# ─── Maintenance ─────────────────────────────────────────────────────────────

@router.post("/{project_id}/maintenance/generate")
async def generate_maintenance(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    service = GenerationService(db)
    return await service.generate_maintenance(project)


@router.get("/{project_id}/maintenance")
def get_maintenance(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "maintenance")


# ─── Helper ──────────────────────────────────────────────────────────────────

def _get_latest_doc(db: Session, project_id: int, doc_type: str):
    doc = db.query(GeneratedDocument).filter(
        GeneratedDocument.project_id == project_id,
        GeneratedDocument.doc_type == doc_type,
        GeneratedDocument.is_latest == True,
    ).first()
    if not doc:
        return {"project_id": project_id, "content": None, "message": "Not yet generated."}
    return {"project_id": project_id, "content": doc.content, "version": doc.version, "generated_at": doc.created_at}
