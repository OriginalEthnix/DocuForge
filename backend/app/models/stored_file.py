from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.core.database import Base


class StoredFile(Base):
    __tablename__ = "stored_files"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer, ForeignKey("projects.id"), nullable=False, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    original_filename = Column(String(255), nullable=False)
    s3_key = Column(String(1024), nullable=False, unique=True)
    content_type = Column(String(255), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())