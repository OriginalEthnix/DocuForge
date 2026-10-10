import re
from pathlib import Path
from uuid import uuid4

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.project import Project
from app.models.stored_file import StoredFile
from app.models.user import User
from app.services.s3_service import upload_bytes, create_download_url, delete_object

router = APIRouter()


def safe_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
    name = name.strip(" .")
    return name[:200] or "upload"


def get_owned_project(db: Session, project_id: int, user_id: int):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    return project


@router.post("/{project_id}/files", status_code=201)
async def upload_project_file(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, project_id, current_user.id)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = await file.read(max_bytes + 1)

    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB limit.",
        )

    filename = safe_filename(file.filename or "upload")
    content_type = file.content_type or "application/octet-stream"
    key = f"users/{current_user.id}/projects/{project_id}/uploads/{uuid4().hex}/{filename}"

    try:
        upload_bytes(content, key, content_type)
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not upload the file to cloud storage.",
        ) from exc
    finally:
        await file.close()

    record = StoredFile(
        project_id=project_id,
        user_id=current_user.id,
        original_filename=filename,
        s3_key=key,
        content_type=content_type,
        size_bytes=len(content),
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception:
        db.rollback()
        try:
            delete_object(key)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Could not save file metadata.")

    try:
        download_url = create_download_url(record.s3_key, record.original_filename)
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The file was stored, but a download link could not be created.",
        ) from exc

    return {
        "id": record.id,
        "filename": record.original_filename,
        "content_type": record.content_type,
        "size_bytes": record.size_bytes,
        "download_url": download_url,
        "expires_in_seconds": settings.S3_PRESIGNED_URL_EXPIRE_SECONDS,
    }


@router.get("/{project_id}/files/{file_id}/download")
def get_project_file_download(
    project_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, project_id, current_user.id)

    record = db.query(StoredFile).filter(
        StoredFile.id == file_id,
        StoredFile.project_id == project_id,
        StoredFile.user_id == current_user.id,
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        url = create_download_url(record.s3_key, record.original_filename)
    except (ClientError, BotoCoreError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not create a download link.",
        ) from exc

    return {
        "id": record.id,
        "filename": record.original_filename,
        "download_url": url,
        "expires_in_seconds": settings.S3_PRESIGNED_URL_EXPIRE_SECONDS,
    }