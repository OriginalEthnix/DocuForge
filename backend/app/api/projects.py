"""
Projects API Router — CRUD for projects
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse

router = APIRouter()


def _get_project_or_404(project_id: int, user: User, db: Session) -> Project:
    """Get a project by ID, ensuring it belongs to the current user."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user.id,
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found.",
        )
    return project


@router.get("", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all projects for the current user with pagination."""
    query = db.query(Project).filter(Project.user_id == current_user.id)

    if status_filter:
        query = query.filter(Project.status == status_filter)

    total = query.count()
    projects = (
        query.order_by(Project.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new project."""
    project = Project(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        problem_statement=payload.problem_statement,
        objectives=payload.objectives,
        domain=payload.domain,
        target_users=payload.target_users,
        tech_stack=payload.tech_stack,
        team_size=payload.team_size,
        timeline_weeks=payload.timeline_weeks,
        stakeholders=payload.stakeholders,
        expected_deliverables=payload.expected_deliverables,
        status="draft",
        completion_percentage=0,
        generated_modules=[],
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Persist project metadata and structure to AWS S3
    _sync_project_to_s3(current_user.id, project)

    return ProjectResponse.model_validate(project)


def _sync_project_to_s3(user_id: int, project: Project) -> None:
    try:
        from app.services.s3_service import sync_project_metadata
        data = {
            "id": project.id,
            "user_id": user_id,
            "title": project.title,
            "description": project.description,
            "problem_statement": project.problem_statement,
            "objectives": project.objectives,
            "domain": project.domain,
            "target_users": project.target_users,
            "tech_stack": project.tech_stack,
            "team_size": project.team_size,
            "timeline_weeks": project.timeline_weeks,
            "stakeholders": project.stakeholders,
            "expected_deliverables": project.expected_deliverables,
            "status": project.status,
            "completion_percentage": project.completion_percentage,
            "generated_modules": project.generated_modules,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        }
        sync_project_metadata(user_id, project.id, data)
    except Exception as exc:
        from app.utils.logger import logger
        logger.warning(f"S3 sync for project {project.id} failed: {exc}")


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific project by ID."""
    project = _get_project_or_404(project_id, current_user, db)
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project's details."""
    project = _get_project_or_404(project_id, current_user, db)

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    # Sync updated project metadata to S3
    _sync_project_to_s3(current_user.id, project)

    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently delete a project and all its data."""
    project = _get_project_or_404(project_id, current_user, db)
    project_id_val = project.id
    user_id_val = current_user.id

    db.delete(project)
    db.commit()

    # Clean up S3 project metadata
    try:
        from app.services.s3_service import delete_project_metadata
        delete_project_metadata(user_id_val, project_id_val)
    except Exception as exc:
        from app.utils.logger import logger
        logger.warning(f"S3 cleanup for deleted project {project_id_val} failed: {exc}")
