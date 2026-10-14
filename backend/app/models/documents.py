"""
Supporting Models — Requirements, UserStories, Diagrams, Risks, TestCases, SprintPlans, GeneratedDocuments
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    req_type = Column(String(50), nullable=False)  # functional, non_functional, business
    req_id = Column(String(20), nullable=True)  # e.g. FR-001
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # high, medium, low
    category = Column(String(100), nullable=True)
    acceptance_criteria = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="requirements")


class UserStory(Base):
    __tablename__ = "user_stories"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    story_id = Column(String(20), nullable=True)  # e.g. US-001
    epic = Column(String(255), nullable=True)
    title = Column(String(500), nullable=False)
    as_a = Column(String(255), nullable=False)
    i_want = Column(Text, nullable=False)
    so_that = Column(Text, nullable=False)
    acceptance_criteria = Column(JSON, default=list)
    story_points = Column(Integer, default=1)
    priority = Column(String(20), default="medium")
    sprint = Column(Integer, nullable=True)
    status = Column(String(50), default="backlog")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="user_stories")


class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    diagram_type = Column(String(50), nullable=False)  # use_case, class, sequence, etc.
    title = Column(String(255), nullable=False)
    plantuml_code = Column(Text, nullable=False)
    svg_content = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # uml or dfd
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="diagrams")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    risk_id = Column(String(20), nullable=True)  # e.g. R-001
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    probability = Column(String(20), nullable=False)  # low, medium, high
    impact = Column(String(20), nullable=False)  # low, medium, high
    risk_level = Column(String(20), nullable=True)  # critical, high, medium, low
    mitigation_strategy = Column(Text, nullable=False)
    contingency_plan = Column(Text, nullable=True)
    owner = Column(String(255), nullable=True)
    status = Column(String(50), default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="risks")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    test_id = Column(String(20), nullable=True)  # e.g. TC-001
    test_type = Column(String(50), nullable=False)  # unit, integration, system, acceptance
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    preconditions = Column(Text, nullable=True)
    test_steps = Column(JSON, default=list)
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=True)
    priority = Column(String(20), default="medium")
    status = Column(String(50), default="not_executed")
    requirement_id = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="test_cases")


class SprintPlan(Base):
    __tablename__ = "sprint_plans"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    sprint_number = Column(Integer, nullable=False)
    sprint_goal = Column(Text, nullable=False)
    duration_weeks = Column(Integer, default=2)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    stories = Column(JSON, default=list)
    milestones = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="sprint_plans")


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(64), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    doc_type = Column(String(100), nullable=False, index=True)  # requirements, user_stories, srs, uml, dfd, database, planning, estimation, risks, tests, traceability, metrics, maintenance
    content = Column(JSON, nullable=False)  # structured JSON content
    s3_key = Column(String(1024), nullable=True, index=True)
    content_type = Column(String(100), default="application/json")
    file_size_bytes = Column(Integer, nullable=True)
    version = Column(Integer, default=1)
    status = Column(String(50), default="completed")
    is_latest = Column(Boolean, default=True, index=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="generated_docs")

