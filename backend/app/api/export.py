"""
Export API Router — PDF export endpoint
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.documents import GeneratedDocument, Requirement, UserStory, Risk, TestCase
from app.services.pdf.pdf_service import generate_project_pdf

router = APIRouter()


@router.get("/{project_id}/export/pdf")
def export_pdf(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export all generated documentation as a professional PDF report."""
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Gather all generated documents
    def get_doc(doc_type: str):
        doc = db.query(GeneratedDocument).filter(
            GeneratedDocument.project_id == project_id,
            GeneratedDocument.doc_type == doc_type,
            GeneratedDocument.is_latest == True,
        ).first()
        return doc.content if doc else None

    # Build docs dict for PDF service
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
    req_data = {"functional": [], "non_functional": [], "business": []}
    for req in requirements:
        item = {"req_id": req.req_id, "title": req.title, "description": req.description,
                "priority": req.priority, "category": req.category}
        key = req.req_type if req.req_type in req_data else "functional"
        req_data[key].append(item)

    user_stories = db.query(UserStory).filter(UserStory.project_id == project_id).all()
    stories_data = {"stories": [
        {"story_id": s.story_id, "epic": s.epic, "as_a": s.as_a,
         "i_want": s.i_want, "story_points": s.story_points, "sprint": s.sprint}
        for s in user_stories
    ]}

    risks = db.query(Risk).filter(Risk.project_id == project_id).all()
    risks_data = {"risks": [
        {"risk_id": r.risk_id, "title": r.title, "probability": r.probability,
         "impact": r.impact, "risk_level": r.risk_level, "owner": r.owner}
        for r in risks
    ]}

    test_cases = db.query(TestCase).filter(TestCase.project_id == project_id).all()
    tests_data = {"test_cases": [
        {"test_id": t.test_id, "test_type": t.test_type, "title": t.title,
         "priority": t.priority, "requirement_id": t.requirement_id}
        for t in test_cases
    ]}

    docs = {
        "requirements": req_data,
        "user_stories": stories_data,
        "srs": get_doc("srs"),
        "estimation": get_doc("estimation"),
        "risks": risks_data,
        "test_cases": tests_data,
        "traceability": get_doc("traceability"),
        "metrics": get_doc("metrics"),
        "maintenance": get_doc("maintenance"),
        "planning": get_doc("planning"),
    }

    pdf_bytes = generate_project_pdf(project, docs)

    filename = f"{project.title.replace(' ', '_')}_Documentation.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
