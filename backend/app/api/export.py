"""
Export API Router — PDF export endpoint
"""
import re
from uuid import uuid4

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.documents import GeneratedDocument, Requirement, UserStory, Risk, TestCase
from app.models.project import Project
from app.models.stored_file import StoredFile
from app.models.user import User
from app.services.pdf.pdf_service import generate_project_pdf
from app.services.s3_service import upload_bytes, create_download_url, delete_object

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
    logger.info(f"PDF generated for project {project_id}: {len(pdf_bytes)} bytes")

    safe_title = re.sub(r"[^A-Za-z0-9_-]", "_", project.title).strip("_")
    safe_title = safe_title[:100] or "Project"
    filename = f"{safe_title}_Documentation.pdf"
    s3_key = (
        f"users/{current_user.id}/projects/{project_id}/generated/"
        f"{uuid4().hex}/{filename}"
    )

    try:
        upload_bytes(pdf_bytes, s3_key, "application/pdf")
        logger.info(f"PDF uploaded to S3: {s3_key}")
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        logger.error(f"S3 upload failed for project {project_id}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The PDF was generated but could not be stored in cloud storage.",
        ) from exc

    record = StoredFile(
        project_id=project_id,
        user_id=current_user.id,
        original_filename=filename,
        s3_key=s3_key,
        content_type="application/pdf",
        size_bytes=len(pdf_bytes),
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(f"File metadata saved: record id={record.id}")
    except Exception as exc:
        db.rollback()
        logger.error(f"DB commit failed for project {project_id}: {exc}")
        try:
            delete_object(s3_key)
            logger.info(f"Cleaned up S3 object after DB failure: {s3_key}")
        except Exception as cleanup_exc:
            logger.warning(f"S3 cleanup failed for key {s3_key}: {cleanup_exc}")
        raise HTTPException(
            status_code=500,
            detail="The PDF was uploaded, but its metadata could not be saved.",
        ) from exc

    try:
        download_url = create_download_url(s3_key, filename)
        logger.info(f"Presigned URL created for record {record.id}")
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        logger.error(f"Presigned URL generation failed for key {s3_key}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The PDF was stored, but a download link could not be created.",
        ) from exc

    return {
        "message": "PDF generated and stored successfully.",
        "file_id": record.id,
        "filename": filename,
        "content_type": "application/pdf",
        "size_bytes": len(pdf_bytes),
        "download_url": download_url,
        "expires_in_seconds": settings.S3_PRESIGNED_URL_EXPIRE_SECONDS,
    }