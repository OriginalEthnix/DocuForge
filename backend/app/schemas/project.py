"""
Pydantic Schemas — Projects
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    problem_statement: Optional[str] = None
    objectives: Optional[str] = None
    domain: str = "web"
    target_users: Optional[str] = None
    tech_stack: List[str] = []
    team_size: int = Field(default=1, ge=1, le=1000)
    timeline_weeks: int = Field(default=12, ge=1, le=520)
    stakeholders: List[str] = []
    expected_deliverables: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Student Management System",
                "description": "A web-based system to manage student records...",
                "domain": "web",
                "tech_stack": ["React", "FastAPI", "PostgreSQL"],
                "team_size": 4,
                "timeline_weeks": 16
            }
        }


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    problem_statement: Optional[str] = None
    objectives: Optional[str] = None
    domain: Optional[str] = None
    target_users: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    team_size: Optional[int] = None
    timeline_weeks: Optional[int] = None
    stakeholders: Optional[List[str]] = None
    expected_deliverables: Optional[List[str]] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    problem_statement: Optional[str] = None
    objectives: Optional[str] = None
    domain: str
    target_users: Optional[str] = None
    tech_stack: List[str] = []
    team_size: int
    timeline_weeks: int
    stakeholders: List[str] = []
    expected_deliverables: List[str] = []
    status: str
    completion_percentage: int
    generated_modules: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int


class DashboardStats(BaseModel):
    total_projects: int
    completed_projects: int
    in_progress_projects: int
    total_documents_generated: int
    recent_projects: List[ProjectResponse]
    completion_rate: float
    modules_generated_this_week: int
