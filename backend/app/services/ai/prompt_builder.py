"""
Prompt Builder — Builds context-rich IEEE-standard prompts for each documentation module.
Every prompt is engineered to produce professional software engineering documentation.
"""
from typing import Any, Dict
from app.models.project import Project


def _project_context(project: Project) -> str:
    """Build the base project context string shared across all prompts."""
    tech_stack = ", ".join(project.tech_stack) if project.tech_stack else "Not specified"
    stakeholders = ", ".join(project.stakeholders) if project.stakeholders else "Not specified"
    deliverables = ", ".join(project.expected_deliverables) if project.expected_deliverables else "Not specified"

    return f"""
PROJECT CONTEXT:
- Title: {project.title}
- Domain: {project.domain}
- Description: {project.description}
- Problem Statement: {project.problem_statement or 'Not provided'}
- Objectives: {project.objectives or 'Not provided'}
- Target Users: {project.target_users or 'Not specified'}
- Technology Stack: {tech_stack}
- Team Size: {project.team_size} developers
- Timeline: {project.timeline_weeks} weeks
- Key Stakeholders: {stakeholders}
- Expected Deliverables: {deliverables}
""".strip()


def build_requirements_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate a comprehensive software requirements document following IEEE 830 standard.

Return a JSON object with this EXACT structure:
{{
  "functional": [
    {{
      "req_id": "FR-001",
      "title": "Short requirement title",
      "description": "Detailed description of what the system shall do",
      "priority": "high|medium|low",
      "category": "Category name (e.g., User Management, Authentication)",
      "acceptance_criteria": "Specific, measurable acceptance criterion"
    }}
  ],
  "non_functional": [
    {{
      "req_id": "NFR-001",
      "title": "Short NFR title",
      "description": "Detailed NFR description with specific measurable targets",
      "priority": "high|medium|low",
      "category": "Performance|Security|Usability|Reliability|Scalability|Maintainability",
      "acceptance_criteria": "Measurable acceptance criterion"
    }}
  ],
  "business": [
    {{
      "req_id": "BR-001",
      "title": "Business requirement title",
      "description": "Business need or constraint",
      "priority": "high|medium|low",
      "category": "Business Rule|Regulatory|Process|Reporting",
      "acceptance_criteria": "Business acceptance criterion"
    }}
  ],
  "stakeholders": ["List of all stakeholders with roles"],
  "assumptions": ["List of project assumptions"],
  "constraints": ["Technical, business, and regulatory constraints"],
  "dependencies": ["External dependencies and integrations"]
}}

Generate at least 15 functional, 8 non-functional, and 5 business requirements. Make them specific and professional.
"""


def build_user_stories_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate comprehensive Agile user stories following best practices.

Return a JSON object with this EXACT structure:
{{
  "stories": [
    {{
      "story_id": "US-001",
      "epic": "Epic name (e.g., User Authentication, Dashboard, Reporting)",
      "title": "Short story title",
      "as_a": "role (e.g., registered user, admin, system)",
      "i_want": "specific feature or capability",
      "so_that": "business value or benefit",
      "acceptance_criteria": [
        "GIVEN ... WHEN ... THEN ...",
        "GIVEN ... WHEN ... THEN ..."
      ],
      "story_points": 1-13,
      "priority": "critical|high|medium|low",
      "sprint": 1-{max(1, project.timeline_weeks // 2)}
    }}
  ],
  "epics": ["List of all epic names"],
  "total_story_points": 0
}}

Generate at least 20 user stories across multiple epics. Use proper Gherkin format for acceptance criteria.
Distribute stories across {max(1, project.timeline_weeks // 2)} sprints logically.
"""


def build_srs_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate a complete IEEE 830 Software Requirements Specification (SRS) document.

Return a JSON object with this EXACT structure:
{{
  "document_info": {{
    "title": "Software Requirements Specification",
    "project_name": "{project.title}",
    "version": "1.0",
    "date": "2025",
    "status": "Draft"
  }},
  "section_1_introduction": {{
    "purpose": "Purpose of this SRS document",
    "document_conventions": "Conventions used in this document",
    "intended_audience": "Who should read this document",
    "project_scope": "Scope of the software being specified",
    "references": ["List of referenced standards and documents"],
    "overview": "Overview of what follows in the document"
  }},
  "section_2_overall_description": {{
    "product_perspective": "Context and origin of the product",
    "product_functions": ["Major functions the product will perform"],
    "user_classes": ["User classes and characteristics"],
    "operating_environment": "Hardware, OS, software environment",
    "design_constraints": ["Implementation and design constraints"],
    "user_documentation": "User documentation to be delivered",
    "assumptions_and_dependencies": ["Assumptions and external dependencies"]
  }},
  "section_3_functional_requirements": [
    {{
      "id": "FR-001",
      "name": "Feature Name",
      "description": "Detailed description",
      "inputs": "Inputs to the feature",
      "processing": "Processing steps",
      "outputs": "Outputs produced",
      "priority": "High|Medium|Low"
    }}
  ],
  "section_4_nonfunctional_requirements": {{
    "performance": ["Performance requirements with specific metrics"],
    "security": ["Security requirements"],
    "usability": ["Usability requirements"],
    "reliability": ["Reliability and availability requirements"],
    "scalability": ["Scalability requirements"],
    "maintainability": ["Maintainability requirements"]
  }},
  "section_5_external_interfaces": {{
    "user_interfaces": "UI requirements",
    "hardware_interfaces": "Hardware interface requirements",
    "software_interfaces": ["Third-party software integrations"],
    "communication_interfaces": ["APIs, protocols, data formats"]
  }},
  "section_6_other_requirements": {{
    "database_requirements": "Database requirements",
    "internationalization": "I18n requirements",
    "legal_requirements": "Legal and compliance requirements",
    "reuse_objectives": "Reusability objectives"
  }},
  "appendix_a_glossary": {{"term": "definition"}},
  "appendix_b_analysis_models": "Description of any analysis models"
}}
"""


def build_uml_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate PlantUML code for 6 UML diagrams for this project.

Return a JSON object:
{{
  "diagrams": [
    {{
      "diagram_type": "use_case",
      "title": "Use Case Diagram",
      "category": "uml",
      "plantuml_code": "@startuml\\n... valid PlantUML code ...\\n@enduml"
    }},
    {{
      "diagram_type": "class",
      "title": "Class Diagram",
      "category": "uml",
      "plantuml_code": "@startuml\\n... valid PlantUML code ...\\n@enduml"
    }},
    {{
      "diagram_type": "sequence",
      "title": "Sequence Diagram - User Authentication",
      "category": "uml",
      "plantuml_code": "@startuml\\n... valid PlantUML code ...\\n@enduml"
    }},
    {{
      "diagram_type": "activity",
      "title": "Activity Diagram - Main Workflow",
      "category": "uml",
      "plantuml_code": "@startuml\\n... valid PlantUML code ...\\n@enduml"
    }},
    {{
      "diagram_type": "component",
      "title": "Component Diagram",
      "category": "uml",
      "plantuml_code": "@startuml\\n... valid PlantUML code ...\\n@enduml"
    }},
    {{
      "diagram_type": "deployment",
      "title": "Deployment Diagram",
      "category": "uml",
      "plantuml_code": "@startuml\\n... valid PlantUML code ...\\n@enduml"
    }}
  ]
}}

Make PlantUML code syntactically valid, detailed, and specific to this project.
Use proper PlantUML syntax with actors, components, classes, and relationships.
"""


def build_dfd_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate PlantUML-style diagrams for Data Flow Diagrams (DFD) at Context, Level 0, and Level 1.

Return a JSON object:
{{
  "diagrams": [
    {{
      "diagram_type": "context_diagram",
      "title": "Context Diagram (Level 0 DFD)",
      "category": "dfd",
      "plantuml_code": "@startuml\\n... use rectangle for processes, database for stores, actor for entities ...\\n@enduml"
    }},
    {{
      "diagram_type": "dfd_level0",
      "title": "DFD Level 0 - System Overview",
      "category": "dfd",
      "plantuml_code": "@startuml\\n...\\n@enduml"
    }},
    {{
      "diagram_type": "dfd_level1",
      "title": "DFD Level 1 - Process Decomposition",
      "category": "dfd",
      "plantuml_code": "@startuml\\n...\\n@enduml"
    }}
  ]
}}
"""


def build_database_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Design a normalized database schema for this project.

Return a JSON object:
{{
  "entities": [
    {{
      "name": "EntityName",
      "description": "What this entity represents",
      "fields": [
        {{
          "name": "field_name",
          "data_type": "INTEGER|VARCHAR(n)|TEXT|BOOLEAN|TIMESTAMP|DECIMAL(p,s)",
          "constraints": ["PRIMARY KEY", "NOT NULL", "UNIQUE", "FOREIGN KEY"],
          "description": "Field purpose"
        }}
      ]
    }}
  ],
  "relationships": [
    {{
      "from_entity": "Entity1",
      "to_entity": "Entity2",
      "relationship_type": "one-to-one|one-to-many|many-to-many",
      "description": "Nature of the relationship"
    }}
  ],
  "er_diagram_plantuml": "@startuml\\n!define Table(name,desc) class name as \\"desc\\" << (T,#FFAAAA) >>\\n... ER diagram code ...\\n@enduml",
  "sql_schema": "-- Complete SQL DDL statements\\nCREATE TABLE ...\\n..."
}}

Design at least 8 normalized tables with proper primary keys, foreign keys, and indexes.
"""


def build_planning_prompt(project: Project) -> str:
    ctx = _project_context(project)
    num_sprints = max(1, project.timeline_weeks // 2)
    return f"""
{ctx}

TASK: Generate a comprehensive Agile project plan for {project.timeline_weeks} weeks with {num_sprints} sprints.

Return a JSON object:
{{
  "product_backlog": [
    {{
      "id": "PB-001",
      "title": "Backlog item title",
      "type": "Epic|Feature|Bug|Technical Debt",
      "priority": "Critical|High|Medium|Low",
      "story_points": 0,
      "status": "Backlog"
    }}
  ],
  "sprints": [
    {{
      "sprint_number": 1,
      "sprint_goal": "Clear sprint goal statement",
      "duration_weeks": 2,
      "stories": ["US-001", "US-002"],
      "milestones": ["Deliverable achieved in this sprint"]
    }}
  ],
  "milestones": [
    {{
      "week": 4,
      "title": "Milestone title",
      "deliverables": ["List of deliverables"]
    }}
  ],
  "gantt_data": [
    {{
      "task": "Task name",
      "start_week": 1,
      "end_week": 4,
      "category": "Phase/Category",
      "dependencies": []
    }}
  ],
  "pert_data": {{
    "nodes": [
      {{"id": "A", "task": "Task name", "duration_days": 14, "earliest_start": 0, "latest_start": 0, "slack": 0}}
    ],
    "critical_path": ["A", "B", "C"],
    "project_duration_days": {project.timeline_weeks * 7}
  }},
  "release_plan": [
    {{
      "release": "v1.0",
      "target_week": {project.timeline_weeks},
      "features": ["List of features in this release"],
      "release_criteria": "Definition of done"
    }}
  ]
}}
"""


def build_estimation_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Perform comprehensive software estimation using multiple methods.

Return a JSON object:
{{
  "cocomo": {{
    "model": "Intermediate COCOMO",
    "mode": "Organic|Semi-detached|Embedded",
    "kloc": 0.0,
    "effort_person_months": 0.0,
    "duration_months": 0.0,
    "team_size_recommended": 0,
    "cost_multipliers": {{"reliability": 1.0, "complexity": 1.0, "experience": 1.0}},
    "calculation_steps": ["Step-by-step COCOMO calculation"],
    "notes": "Assumptions and notes"
  }},
  "function_point": {{
    "inputs": 0, "outputs": 0, "inquiries": 0, "files": 0, "interfaces": 0,
    "unadjusted_fps": 0,
    "complexity_factor": 1.0,
    "adjusted_fps": 0.0,
    "productivity_rate": 0.0,
    "person_months": 0.0,
    "calculation_steps": ["Step-by-step FPA calculation"]
  }},
  "time_estimation": {{
    "optimistic_weeks": 0,
    "most_likely_weeks": 0,
    "pessimistic_weeks": 0,
    "pert_estimate_weeks": 0.0,
    "standard_deviation_weeks": 0.0,
    "confidence_95_percent": "{{low}} - {{high}} weeks"
  }},
  "cost_estimation": {{
    "currency": "USD",
    "avg_developer_monthly_cost": 5000,
    "total_person_months": 0.0,
    "development_cost": 0.0,
    "infrastructure_cost": 0.0,
    "testing_cost": 0.0,
    "contingency_15_percent": 0.0,
    "total_estimated_cost": 0.0,
    "cost_breakdown": {{}}
  }},
  "team_estimation": {{
    "recommended_team_size": {project.team_size},
    "roles": [
      {{"role": "Role name", "count": 1, "responsibilities": "Key responsibilities"}}
    ],
    "productivity_metrics": {{
      "velocity_points_per_sprint": 0,
      "defect_rate_percent": 0.0,
      "code_coverage_target": 0
    }}
  }},
  "summary": "Executive summary of all estimation results with recommendations"
}}
"""


def build_risk_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate a comprehensive risk register and risk matrix.

Return a JSON object:
{{
  "risks": [
    {{
      "risk_id": "R-001",
      "title": "Risk title",
      "description": "Detailed risk description",
      "category": "Technical|Schedule|Resource|Business|External|Security",
      "probability": "low|medium|high",
      "impact": "low|medium|high",
      "risk_level": "critical|high|medium|low",
      "mitigation_strategy": "Specific mitigation actions",
      "contingency_plan": "What to do if risk materializes",
      "owner": "Risk owner role",
      "status": "open|mitigated|closed|accepted"
    }}
  ],
  "risk_matrix": {{
    "critical": ["Risk IDs"],
    "high": ["Risk IDs"],
    "medium": ["Risk IDs"],
    "low": ["Risk IDs"],
    "heatmap_data": [
      {{"probability": "high", "impact": "high", "risks": []}},
      {{"probability": "high", "impact": "medium", "risks": []}},
      {{"probability": "medium", "impact": "high", "risks": []}}
    ]
  }},
  "summary": "Overall risk assessment and top priorities"
}}

Generate at least 15 risks covering all categories. Be specific and professional.
"""


def build_test_cases_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate comprehensive test cases covering all testing levels.

Return a JSON object:
{{
  "test_cases": [
    {{
      "test_id": "TC-001",
      "test_type": "unit|integration|system|acceptance|regression|boundary",
      "title": "Test case title",
      "description": "What this test validates",
      "preconditions": "Setup conditions required",
      "test_steps": [
        "Step 1: Action",
        "Step 2: Action"
      ],
      "expected_result": "Expected outcome",
      "priority": "critical|high|medium|low",
      "requirement_id": "FR-001"
    }}
  ],
  "summary": {{
    "unit": 0,
    "integration": 0,
    "system": 0,
    "acceptance": 0,
    "regression": 0,
    "boundary": 0,
    "total": 0
  }}
}}

Generate at least 30 test cases across all types. Include both positive and negative test cases, boundary conditions.
"""


def build_traceability_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate a Requirements Traceability Matrix (RTM) mapping requirements through the entire SDLC.

Return a JSON object:
{{
  "matrix": [
    {{
      "requirement_id": "FR-001",
      "requirement_title": "Requirement name",
      "design_component": "Which design component addresses this",
      "implementation_module": "Which code module implements this",
      "test_case_ids": ["TC-001", "TC-002"],
      "test_status": "Not Tested|Pass|Fail|In Progress",
      "maintenance_notes": "Maintenance considerations",
      "coverage_status": "covered|partially_covered|not_covered"
    }}
  ],
  "coverage_percentage": 0.0,
  "summary": {{
    "total_requirements": 0,
    "covered": 0,
    "partially_covered": 0,
    "not_covered": 0
  }}
}}

Create matrix entries for at least 20 requirements covering functional and non-functional requirements.
"""


def build_metrics_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate a software quality metrics dashboard with realistic values.

Return a JSON object:
{{
  "metrics": {{
    "cyclomatic_complexity": {{
      "average": 0.0, "max": 0, "threshold": 10,
      "status": "good|warning|critical",
      "description": "Explanation of cyclomatic complexity for this project"
    }},
    "defect_density": {{
      "value": 0.0, "unit": "defects/KLOC",
      "status": "good|warning|critical",
      "description": "Expected defect density"
    }},
    "maintainability_index": {{
      "value": 0.0, "max": 100,
      "status": "good|warning|critical",
      "description": "Maintainability assessment"
    }},
    "requirement_coverage": {{
      "covered_percentage": 0.0,
      "implemented": 0, "total": 0,
      "status": "good|warning|critical"
    }},
    "requirement_stability": {{
      "change_rate_percentage": 0.0,
      "baseline_requirements": 0, "changes": 0,
      "status": "stable|unstable"
    }},
    "code_coverage_target": {{
      "target_percentage": 80,
      "current_percentage": 0,
      "unit_test_coverage": 0, "integration_coverage": 0
    }},
    "productivity": {{
      "story_points_per_sprint": 0,
      "velocity_trend": "increasing|stable|decreasing",
      "features_per_week": 0.0
    }},
    "technical_debt": {{
      "estimated_hours": 0,
      "debt_ratio_percentage": 0.0,
      "priority_areas": ["List of technical debt areas"]
    }}
  }},
  "charts_data": {{
    "quality_radar": {{
      "labels": ["Reliability", "Usability", "Efficiency", "Maintainability", "Portability"],
      "values": [0, 0, 0, 0, 0]
    }},
    "defect_trend": {{
      "labels": ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4"],
      "values": [0, 0, 0, 0]
    }},
    "coverage_progress": {{
      "labels": ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4"],
      "values": [0, 0, 0, 0]
    }}
  }}
}}
"""


def build_maintenance_prompt(project: Project) -> str:
    ctx = _project_context(project)
    return f"""
{ctx}

TASK: Generate a comprehensive software maintenance plan following IEEE standards.

Return a JSON object:
{{
  "overview": {{
    "maintenance_approach": "Description of overall maintenance strategy",
    "support_model": "Support model description",
    "maintenance_team": "Team structure for maintenance",
    "contact_matrix": [
      {{"role": "Role", "responsibility": "What they handle", "escalation_level": 1}}
    ]
  }},
  "corrective_maintenance": {{
    "description": "How bugs and defects will be fixed",
    "process": ["Step-by-step corrective maintenance process"],
    "sla": {{
      "critical_bugs": "4 hours",
      "high_bugs": "24 hours",
      "medium_bugs": "72 hours",
      "low_bugs": "1 week"
    }},
    "tools": ["List of tools for issue tracking and fixing"]
  }},
  "adaptive_maintenance": {{
    "description": "How the system adapts to environment changes",
    "triggers": ["List of triggers for adaptive maintenance"],
    "process": ["Adaptive maintenance process steps"],
    "examples": ["Example scenarios requiring adaptive maintenance"]
  }},
  "preventive_maintenance": {{
    "description": "Proactive maintenance to prevent issues",
    "schedule": [
      {{"activity": "Activity name", "frequency": "Weekly|Monthly|Quarterly", "responsible": "Team/Role"}}
    ],
    "code_review_policy": "Code review standards",
    "refactoring_guidelines": "When and how to refactor"
  }},
  "perfective_maintenance": {{
    "description": "Improvements and enhancements",
    "enhancement_process": ["Process for requesting and implementing enhancements"],
    "roadmap": [
      {{"version": "v1.1", "planned_features": ["Features list"], "target_quarter": "Q1 2026"}}
    ]
  }},
  "maintenance_metrics": {{
    "mttr": "Mean Time To Repair target",
    "mtbf": "Mean Time Between Failures target",
    "availability_target": "99.5%",
    "change_success_rate": "95%"
  }},
  "documentation_maintenance": {{
    "update_triggers": ["When to update documentation"],
    "documentation_owner": "Who maintains docs",
    "review_cycle": "Quarterly"
  }}
}}
"""
