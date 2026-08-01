"""
Project Model — SQLAlchemy ORM
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectDomain(str, enum.Enum):
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    EMBEDDED = "embedded"
    AI_ML = "ai_ml"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    ECOMMERCE = "ecommerce"
    EDUCATION = "education"
    OTHER = "other"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Basic Info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    problem_statement = Column(Text, nullable=True)
    objectives = Column(Text, nullable=True)
    domain = Column(String(100), default="web")
    target_users = Column(Text, nullable=True)

    # Technical Details
    tech_stack = Column(JSON, default=list)  # list of strings
    team_size = Column(Integer, default=1)
    timeline_weeks = Column(Integer, default=12)
    stakeholders = Column(JSON, default=list)
    expected_deliverables = Column(JSON, default=list)

    # Status & Progress
    status = Column(String(50), default=ProjectStatus.DRAFT)
    completion_percentage = Column(Integer, default=0)
    generated_modules = Column(JSON, default=list)  # list of completed modules

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="projects")
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    user_stories = relationship("UserStory", back_populates="project", cascade="all, delete-orphan")
    diagrams = relationship("Diagram", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")
    sprint_plans = relationship("SprintPlan", back_populates="project", cascade="all, delete-orphan")
    generated_docs = relationship("GeneratedDocument", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project id={self.id} title={self.title}>"
