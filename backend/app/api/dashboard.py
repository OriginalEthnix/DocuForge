"""
Dashboard API Router — Stats and metrics for the dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.documents import GeneratedDocument

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics for the current user."""
    # Count projects by status
    total = db.query(Project).filter(Project.user_id == current_user.id).count()
    completed = db.query(Project).filter(
        Project.user_id == current_user.id, Project.status == "completed"
    ).count()
    in_progress = db.query(Project).filter(
        Project.user_id == current_user.id, Project.status == "in_progress"
    ).count()
    draft = db.query(Project).filter(
        Project.user_id == current_user.id, Project.status == "draft"
    ).count()

    # Recent projects (last 5)
    recent_projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.updated_at.desc(), Project.created_at.desc())
        .limit(5)
        .all()
    )

    # Total generated documents
    total_docs = db.query(GeneratedDocument).join(Project).filter(
        Project.user_id == current_user.id,
        GeneratedDocument.is_latest == True
    ).count()

    # Documents generated this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    docs_this_week = db.query(GeneratedDocument).join(Project).filter(
        Project.user_id == current_user.id,
        GeneratedDocument.created_at >= week_ago,
    ).count()

    # Completion rate
    completion_rate = round((completed / total * 100) if total > 0 else 0, 1)

    # Module completion breakdown across all projects
    all_projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    module_counts = {}
    for p in all_projects:
        for m in (p.generated_modules or []):
            module_counts[m] = module_counts.get(m, 0) + 1

    return {
        "total_projects": total,
        "completed_projects": completed,
        "in_progress_projects": in_progress,
        "draft_projects": draft,
        "total_documents_generated": total_docs,
        "documents_this_week": docs_this_week,
        "completion_rate": completion_rate,
        "recent_projects": [
            {
                "id": p.id,
                "title": p.title,
                "domain": p.domain,
                "status": p.status,
                "completion_percentage": p.completion_percentage,
                "generated_modules": p.generated_modules or [],
                "tech_stack": p.tech_stack or [],
                "team_size": p.team_size,
                "timeline_weeks": p.timeline_weeks,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in recent_projects
        ],
        "module_popularity": module_counts,
    }
