"""
AI Generation API Router — All 13 generation endpoints, document management, and S3 downloads
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.documents import Requirement, UserStory, Diagram, Risk, TestCase, GeneratedDocument
from app.services.generation_service import GenerationService
from app.services.s3_service import create_download_url, is_s3_error

router = APIRouter()


class DocumentUpdateRequest(BaseModel):
    content: Dict[str, Any]


def _get_project_or_404(project_id: int, user: User, db: Session) -> Project:
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied.")
    return project


def _get_latest_doc(db: Session, project_id: int, doc_type: str) -> Dict[str, Any]:
    doc = db.query(GeneratedDocument).filter(
        GeneratedDocument.project_id == project_id,
        GeneratedDocument.doc_type == doc_type,
        GeneratedDocument.is_latest == True,
    ).first()
    if not doc:
        return {"project_id": project_id, "content": None, "message": "Not yet generated."}

    download_url = None
    if doc.s3_key:
        try:
            download_url = create_download_url(doc.s3_key, f"{doc_type}_v{doc.version}.json")
        except Exception as e:
            logger.warning(f"Failed to generate download URL for doc {doc.id}: {e}")

    return {
        "project_id": project_id,
        "document_id": doc.document_id,
        "doc_type": doc.doc_type,
        "content": doc.content,
        "version": doc.version,
        "s3_key": doc.s3_key,
        "download_url": download_url,
        "status": doc.status,
        "generated_at": doc.created_at.isoformat() if doc.created_at else None,
    }


# ─── 1. Requirements ──────────────────────────────────────────────────────────

@router.post("/{project_id}/requirements/generate")
async def generate_requirements(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_requirements(project)
    except Exception as e:
        logger.error(f"Requirements generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Requirements generation failed: {str(e)}"
        )


@router.get("/{project_id}/requirements")
def get_requirements(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
    latest_doc = _get_latest_doc(db, project_id, "requirements")

    result = {
        "project_id": project_id,
        "document_id": latest_doc.get("document_id"),
        "version": latest_doc.get("version"),
        "s3_key": latest_doc.get("s3_key"),
        "download_url": latest_doc.get("download_url"),
        "functional": [],
        "non_functional": [],
        "business": [],
        "stakeholders": [],
        "assumptions": [],
        "constraints": [],
        "dependencies": [],
    }

    if latest_doc.get("content"):
        c = latest_doc["content"]
        result["stakeholders"] = c.get("stakeholders", [])
        result["assumptions"] = c.get("assumptions", [])
        result["constraints"] = c.get("constraints", [])
        result["dependencies"] = c.get("dependencies", [])

    for req in requirements:
        item = {
            "id": req.id, "req_id": req.req_id, "title": req.title,
            "description": req.description, "priority": req.priority,
            "category": req.category, "acceptance_criteria": req.acceptance_criteria,
        }
        key = req.req_type if req.req_type in result else "functional"
        result[key].append(item)

    return result


# ─── 2. User Stories ──────────────────────────────────────────────────────────

@router.post("/{project_id}/user-stories/generate")
async def generate_user_stories(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_user_stories(project)
    except Exception as e:
        logger.error(f"User stories generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User stories generation failed: {str(e)}"
        )


@router.get("/{project_id}/user-stories")
def get_user_stories(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    stories = db.query(UserStory).filter(UserStory.project_id == project_id).all()
    latest_doc = _get_latest_doc(db, project_id, "user_stories")

    return {
        "project_id": project_id,
        "document_id": latest_doc.get("document_id"),
        "version": latest_doc.get("version"),
        "s3_key": latest_doc.get("s3_key"),
        "download_url": latest_doc.get("download_url"),
        "stories": [
            {
                "id": s.id, "story_id": s.story_id, "epic": s.epic, "title": s.title,
                "as_a": s.as_a, "i_want": s.i_want, "so_that": s.so_that,
                "acceptance_criteria": s.acceptance_criteria, "story_points": s.story_points,
                "priority": s.priority, "sprint": s.sprint, "status": s.status,
            }
            for s in stories
        ],
        "total_story_points": sum(s.story_points or 0 for s in stories),
    }


# ─── 3. SRS ───────────────────────────────────────────────────────────────────

@router.post("/{project_id}/srs/generate")
async def generate_srs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_srs(project)
    except Exception as e:
        logger.error(f"SRS generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SRS generation failed: {str(e)}"
        )


@router.get("/{project_id}/srs")
def get_srs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "srs")


# ─── 4 & 5. Diagrams (UML & DFD) ─────────────────────────────────────────────

@router.post("/{project_id}/diagrams/uml/generate")
async def generate_uml(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_diagrams(project, "uml")
    except Exception as e:
        logger.error(f"UML generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"UML generation failed: {str(e)}"
        )


@router.post("/{project_id}/diagrams/dfd/generate")
async def generate_dfd(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_diagrams(project, "dfd")
    except Exception as e:
        logger.error(f"DFD generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DFD generation failed: {str(e)}"
        )


@router.get("/{project_id}/diagrams")
def get_diagrams(
    project_id: int,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    query = db.query(Diagram).filter(Diagram.project_id == project_id)
    if category:
        query = query.filter(Diagram.category == category)
    diagrams = query.all()

    doc_type = f"{category}_diagrams" if category else "uml_diagrams"
    latest_doc = _get_latest_doc(db, project_id, doc_type)

    return {
        "project_id": project_id,
        "document_id": latest_doc.get("document_id"),
        "version": latest_doc.get("version"),
        "s3_key": latest_doc.get("s3_key"),
        "download_url": latest_doc.get("download_url"),
        "diagrams": [
            {
                "id": d.id, "diagram_type": d.diagram_type, "title": d.title,
                "plantuml_code": d.plantuml_code, "svg_content": d.svg_content,
                "category": d.category,
            }
            for d in diagrams
        ],
    }


# ─── 6. Database Design ───────────────────────────────────────────────────────

@router.post("/{project_id}/database/generate")
async def generate_database(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_database_design(project)
    except Exception as e:
        logger.error(f"Database generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database design generation failed: {str(e)}"
        )


@router.get("/{project_id}/database")
def get_database(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "database_design")


# ─── 7. Project Planning ─────────────────────────────────────────────────────

@router.post("/{project_id}/planning/generate")
async def generate_planning(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_planning(project)
    except Exception as e:
        logger.error(f"Planning generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Planning generation failed: {str(e)}"
        )


@router.get("/{project_id}/planning")
def get_planning(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "planning")


# ─── 8. Estimation ────────────────────────────────────────────────────────────

@router.post("/{project_id}/estimation/generate")
async def generate_estimation(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_estimation(project)
    except Exception as e:
        logger.error(f"Estimation generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Estimation generation failed: {str(e)}"
        )


@router.get("/{project_id}/estimation")
def get_estimation(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "estimation")


# ─── 9. Risk Management ───────────────────────────────────────────────────────

@router.post("/{project_id}/risks/generate")
async def generate_risks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_risks(project)
    except Exception as e:
        logger.error(f"Risk generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk generation failed: {str(e)}"
        )


@router.get("/{project_id}/risks")
def get_risks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    risks = db.query(Risk).filter(Risk.project_id == project_id).all()
    latest_doc = _get_latest_doc(db, project_id, "risks")

    return {
        "project_id": project_id,
        "document_id": latest_doc.get("document_id"),
        "version": latest_doc.get("version"),
        "s3_key": latest_doc.get("s3_key"),
        "download_url": latest_doc.get("download_url"),
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


# ─── 10. Test Cases ───────────────────────────────────────────────────────────

@router.post("/{project_id}/tests/generate")
async def generate_tests(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_test_cases(project)
    except Exception as e:
        logger.error(f"Test cases generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test cases generation failed: {str(e)}"
        )


@router.get("/{project_id}/tests")
def get_tests(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    cases = db.query(TestCase).filter(TestCase.project_id == project_id).all()
    latest_doc = _get_latest_doc(db, project_id, "test_cases")

    return {
        "project_id": project_id,
        "document_id": latest_doc.get("document_id"),
        "version": latest_doc.get("version"),
        "s3_key": latest_doc.get("s3_key"),
        "download_url": latest_doc.get("download_url"),
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


# ─── 11. Traceability ─────────────────────────────────────────────────────────

@router.post("/{project_id}/traceability/generate")
async def generate_traceability(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_traceability(project)
    except Exception as e:
        logger.error(f"Traceability generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Traceability generation failed: {str(e)}"
        )


@router.get("/{project_id}/traceability")
def get_traceability(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "traceability")


# ─── 12. Quality Metrics ──────────────────────────────────────────────────────

@router.post("/{project_id}/metrics/generate")
async def generate_metrics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_metrics(project)
    except Exception as e:
        logger.error(f"Metrics generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics generation failed: {str(e)}"
        )


@router.get("/{project_id}/metrics")
def get_metrics(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "metrics")


# ─── 13. Maintenance ──────────────────────────────────────────────────────────

@router.post("/{project_id}/maintenance/generate")
async def generate_maintenance(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, current_user, db)
    try:
        service = GenerationService(db)
        return await service.generate_maintenance(project)
    except Exception as e:
        logger.error(f"Maintenance generation failed for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Maintenance generation failed: {str(e)}"
        )


@router.get("/{project_id}/maintenance")
def get_maintenance(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, current_user, db)
    return _get_latest_doc(db, project_id, "maintenance")


# ─── Unified Document Management Endpoints (Section 6) ─────────────────────────

@router.get("/{project_id}/documents")
def list_project_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all generated documents and version records for a project."""
    _get_project_or_404(project_id, current_user, db)
    docs = db.query(GeneratedDocument).filter(
        GeneratedDocument.project_id == project_id
    ).order_by(GeneratedDocument.doc_type, GeneratedDocument.version.desc()).all()

    items = []
    for d in docs:
        dl_url = None
        if d.s3_key:
            try:
                dl_url = create_download_url(d.s3_key, f"{d.doc_type}_v{d.version}.json")
            except Exception:
                pass
        items.append({
            "id": d.id,
            "document_id": d.document_id,
            "project_id": d.project_id,
            "doc_type": d.doc_type,
            "s3_key": d.s3_key,
            "version": d.version,
            "is_latest": d.is_latest,
            "content_type": d.content_type,
            "file_size_bytes": d.file_size_bytes,
            "status": d.status,
            "download_url": dl_url,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        })
    return {"project_id": project_id, "documents": items}


@router.get("/{project_id}/documents/{document_id}")
def get_project_document_by_id(
    project_id: int,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific generated document by its document ID."""
    _get_project_or_404(project_id, current_user, db)
    doc = db.query(GeneratedDocument).filter(
        GeneratedDocument.project_id == project_id,
        GeneratedDocument.document_id == document_id,
    ).first()

    if not doc:
        # Fallback to integer primary key lookup if numeric
        if document_id.isdigit():
            doc = db.query(GeneratedDocument).filter(
                GeneratedDocument.project_id == project_id,
                GeneratedDocument.id == int(document_id),
            ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    dl_url = None
    if doc.s3_key:
        try:
            dl_url = create_download_url(doc.s3_key, f"{doc.doc_type}_v{doc.version}.json")
        except Exception:
            pass

    return {
        "id": doc.id,
        "document_id": doc.document_id,
        "project_id": doc.project_id,
        "doc_type": doc.doc_type,
        "s3_key": doc.s3_key,
        "version": doc.version,
        "is_latest": doc.is_latest,
        "content": doc.content,
        "download_url": dl_url,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }


@router.put("/{project_id}/documents/{document_id}")
def update_project_document(
    project_id: int,
    document_id: str,
    payload: DocumentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a document content, persisting a new version to S3 and database."""
    project = _get_project_or_404(project_id, current_user, db)
    existing = db.query(GeneratedDocument).filter(
        GeneratedDocument.project_id == project_id,
        GeneratedDocument.document_id == document_id,
    ).first()

    if not existing:
        if document_id.isdigit():
            existing = db.query(GeneratedDocument).filter(
                GeneratedDocument.project_id == project_id,
                GeneratedDocument.id == int(document_id),
            ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Document not found.")

    service = GenerationService(db)
    result = service._persist_and_upload(
        project=project,
        doc_type=existing.doc_type,
        content=payload.content,
        feature_key=existing.doc_type,
    )
    return result


@router.post("/{project_id}/documents/{document_id}/regenerate")
async def regenerate_project_document(
    project_id: int,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Regenerate a specific document type while keeping historical versions."""
    project = _get_project_or_404(project_id, current_user, db)
    existing = db.query(GeneratedDocument).filter(
        GeneratedDocument.project_id == project_id,
        GeneratedDocument.document_id == document_id,
    ).first()

    if not existing:
        if document_id.isdigit():
            existing = db.query(GeneratedDocument).filter(
                GeneratedDocument.project_id == project_id,
                GeneratedDocument.id == int(document_id),
            ).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Document not found.")

    service = GenerationService(db)
    handlers = {
        "requirements": service.generate_requirements,
        "user_stories": service.generate_user_stories,
        "srs": service.generate_srs,
        "uml_diagrams": lambda p: service.generate_diagrams(p, "uml"),
        "dfd_diagrams": lambda p: service.generate_diagrams(p, "dfd"),
        "database_design": service.generate_database_design,
        "planning": service.generate_planning,
        "estimation": service.generate_estimation,
        "risks": service.generate_risks,
        "test_cases": service.generate_test_cases,
        "traceability": service.generate_traceability,
        "metrics": service.generate_metrics,
        "maintenance": service.generate_maintenance,
    }

    handler = handlers.get(existing.doc_type)
    if not handler:
        raise HTTPException(status_code=400, detail=f"Unsupported document type: {existing.doc_type}")

    return await handler(project)


@router.get("/{project_id}/documents/{document_id}/download")
def download_project_document(
    project_id: int,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a short-lived presigned download link for the document artifact in S3."""
    _get_project_or_404(project_id, current_user, db)
    doc = db.query(GeneratedDocument).filter(
        GeneratedDocument.project_id == project_id,
        GeneratedDocument.document_id == document_id,
    ).first()

    if not doc and document_id.isdigit():
        doc = db.query(GeneratedDocument).filter(
            GeneratedDocument.project_id == project_id,
            GeneratedDocument.id == int(document_id),
        ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if not doc.s3_key:
        raise HTTPException(status_code=404, detail="Document has no S3 storage key.")

    try:
        url = create_download_url(doc.s3_key, f"{doc.doc_type}_v{doc.version}.json")
    except Exception as exc:
        logger.error(f"Failed to generate download URL: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not generate download link for cloud storage.",
        ) from exc

    return {
        "document_id": doc.document_id,
        "filename": f"{doc.doc_type}_v{doc.version}.json",
        "download_url": url,
        "expires_in_seconds": 900,
    }
