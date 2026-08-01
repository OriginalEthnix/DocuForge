"""
Pydantic Schemas — AI Generation Responses
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# ─── Requirements ───────────────────────────────────────────────────────────

class RequirementItem(BaseModel):
    req_id: str
    title: str
    description: str
    priority: str
    category: str
    acceptance_criteria: Optional[str] = None


class RequirementsResponse(BaseModel):
    project_id: int
    functional: List[RequirementItem]
    non_functional: List[RequirementItem]
    business: List[RequirementItem]
    stakeholders: List[str]
    assumptions: List[str]
    constraints: List[str]
    dependencies: List[str]
    generated_at: datetime


# ─── User Stories ────────────────────────────────────────────────────────────

class UserStoryItem(BaseModel):
    story_id: str
    epic: str
    title: str
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: List[str]
    story_points: int
    priority: str
    sprint: int


class UserStoriesResponse(BaseModel):
    project_id: int
    stories: List[UserStoryItem]
    epics: List[str]
    total_story_points: int
    generated_at: datetime


# ─── SRS ─────────────────────────────────────────────────────────────────────

class SRSResponse(BaseModel):
    project_id: int
    content: Dict[str, Any]  # Full IEEE SRS structure
    version: int
    generated_at: datetime


# ─── Diagrams ────────────────────────────────────────────────────────────────

class DiagramItem(BaseModel):
    id: int
    diagram_type: str
    title: str
    plantuml_code: str
    svg_content: Optional[str] = None
    category: str


class DiagramsResponse(BaseModel):
    project_id: int
    diagrams: List[DiagramItem]
    generated_at: datetime


# ─── Database Design ─────────────────────────────────────────────────────────

class EntityField(BaseModel):
    name: str
    data_type: str
    constraints: List[str]
    description: str


class EntityDefinition(BaseModel):
    name: str
    description: str
    fields: List[EntityField]


class RelationshipDefinition(BaseModel):
    from_entity: str
    to_entity: str
    relationship_type: str  # one-to-one, one-to-many, many-to-many
    description: str


class DatabaseDesignResponse(BaseModel):
    project_id: int
    entities: List[EntityDefinition]
    relationships: List[RelationshipDefinition]
    er_diagram_plantuml: str
    sql_schema: str
    generated_at: datetime


# ─── Planning ────────────────────────────────────────────────────────────────

class MilestoneItem(BaseModel):
    week: int
    title: str
    deliverables: List[str]


class SprintItem(BaseModel):
    sprint_number: int
    sprint_goal: str
    duration_weeks: int
    stories: List[str]
    milestones: List[str]


class PlanningResponse(BaseModel):
    project_id: int
    product_backlog: List[Dict[str, Any]]
    sprints: List[SprintItem]
    milestones: List[MilestoneItem]
    gantt_data: List[Dict[str, Any]]
    pert_data: Dict[str, Any]
    release_plan: List[Dict[str, Any]]
    generated_at: datetime


# ─── Estimation ──────────────────────────────────────────────────────────────

class EstimationResponse(BaseModel):
    project_id: int
    cocomo: Dict[str, Any]
    function_point: Dict[str, Any]
    time_estimation: Dict[str, Any]
    cost_estimation: Dict[str, Any]
    team_estimation: Dict[str, Any]
    summary: str
    generated_at: datetime


# ─── Risk Register ───────────────────────────────────────────────────────────

class RiskItem(BaseModel):
    risk_id: str
    title: str
    description: str
    category: str
    probability: str
    impact: str
    risk_level: str
    mitigation_strategy: str
    contingency_plan: str
    owner: str
    status: str


class RiskResponse(BaseModel):
    project_id: int
    risks: List[RiskItem]
    risk_matrix: Dict[str, Any]
    summary: str
    generated_at: datetime


# ─── Test Cases ──────────────────────────────────────────────────────────────

class TestCaseItem(BaseModel):
    test_id: str
    test_type: str
    title: str
    description: str
    preconditions: str
    test_steps: List[str]
    expected_result: str
    priority: str
    requirement_id: Optional[str] = None


class TestCasesResponse(BaseModel):
    project_id: int
    test_cases: List[TestCaseItem]
    summary: Dict[str, int]  # counts by type
    generated_at: datetime


# ─── Traceability Matrix ──────────────────────────────────────────────────────

class TraceabilityResponse(BaseModel):
    project_id: int
    matrix: List[Dict[str, Any]]
    coverage_percentage: float
    generated_at: datetime


# ─── Quality Metrics ─────────────────────────────────────────────────────────

class MetricsResponse(BaseModel):
    project_id: int
    metrics: Dict[str, Any]
    charts_data: Dict[str, Any]
    generated_at: datetime


# ─── Maintenance Plan ────────────────────────────────────────────────────────

class MaintenanceResponse(BaseModel):
    project_id: int
    content: Dict[str, Any]
    generated_at: datetime
