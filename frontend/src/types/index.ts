// ─── Shared Types ─────────────────────────────────────────────────────────────

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  organization?: string;
  avatar_url?: string;
  bio?: string;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// ─── Projects ─────────────────────────────────────────────────────────────────

export type ProjectStatus = 'draft' | 'in_progress' | 'completed' | 'archived';
export type ProjectDomain =
  | 'web' | 'mobile' | 'desktop' | 'embedded'
  | 'ai_ml' | 'fintech' | 'healthcare' | 'ecommerce' | 'education' | 'other';

export interface Project {
  id: number;
  user_id: number;
  title: string;
  description: string;
  problem_statement?: string;
  objectives?: string;
  domain: ProjectDomain;
  target_users?: string;
  tech_stack: string[];
  team_size: number;
  timeline_weeks: number;
  stakeholders: string[];
  expected_deliverables: string[];
  status: ProjectStatus;
  completion_percentage: number;
  generated_modules: string[];
  created_at: string;
  updated_at?: string;
}

export interface ProjectCreate {
  title: string;
  description: string;
  problem_statement?: string;
  objectives?: string;
  domain: ProjectDomain;
  target_users?: string;
  tech_stack: string[];
  team_size: number;
  timeline_weeks: number;
  stakeholders: string[];
  expected_deliverables: string[];
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export interface DashboardStats {
  total_projects: number;
  completed_projects: number;
  in_progress_projects: number;
  draft_projects: number;
  total_documents_generated: number;
  documents_this_week: number;
  completion_rate: number;
  recent_projects: Project[];
  module_popularity: Record<string, number>;
}

// ─── Generation Modules ───────────────────────────────────────────────────────

export interface Requirement {
  id?: number;
  req_id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
  acceptance_criteria?: string;
}

export interface RequirementsData {
  project_id: number;
  functional: Requirement[];
  non_functional: Requirement[];
  business: Requirement[];
  stakeholders: string[];
  assumptions: string[];
  constraints: string[];
  dependencies: string[];
  generated_at?: string;
}

export interface UserStory {
  id?: number;
  story_id: string;
  epic: string;
  title: string;
  as_a: string;
  i_want: string;
  so_that: string;
  acceptance_criteria: string[];
  story_points: number;
  priority: string;
  sprint: number;
  status?: string;
}

export interface UserStoriesData {
  project_id: number;
  stories: UserStory[];
  epics?: string[];
  total_story_points: number;
  generated_at?: string;
}

export interface Diagram {
  id: number;
  diagram_type: string;
  title: string;
  plantuml_code: string;
  svg_content?: string;
  category: string;
}

export interface DiagramsData {
  project_id: number;
  diagrams: Diagram[];
  generated_at?: string;
}

export interface RiskItem {
  id?: number;
  risk_id: string;
  title: string;
  description: string;
  category: string;
  probability: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  mitigation_strategy: string;
  contingency_plan: string;
  owner: string;
  status: string;
}

export interface RisksData {
  project_id: number;
  risks: RiskItem[];
  risk_matrix?: any;
  summary?: string;
  generated_at?: string;
}

export interface TestCaseItem {
  id?: number;
  test_id: string;
  test_type: string;
  title: string;
  description: string;
  preconditions: string;
  test_steps: string[];
  expected_result: string;
  priority: string;
  status?: string;
  requirement_id?: string;
}

export interface TestCasesData {
  project_id: number;
  test_cases: TestCaseItem[];
  summary?: Record<string, number>;
  generated_at?: string;
}

export interface SprintItem {
  sprint_number: number;
  sprint_goal: string;
  duration_weeks: number;
  stories: string[];
  milestones: string[];
}

export interface PlanningData {
  project_id: number;
  product_backlog: any[];
  sprints: SprintItem[];
  milestones: any[];
  gantt_data: any[];
  pert_data: any;
  release_plan: any[];
  generated_at?: string;
}

export interface EstimationData {
  project_id: number;
  cocomo: any;
  function_point: any;
  time_estimation: any;
  cost_estimation: any;
  team_estimation: any;
  summary: string;
  generated_at?: string;
}

export interface MetricsData {
  project_id: number;
  metrics: Record<string, any>;
  charts_data: Record<string, any>;
  generated_at?: string;
}

// ─── API Response ─────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
  status_code?: number;
}

export type GenerationModule =
  | 'requirements' | 'user_stories' | 'srs'
  | 'uml_diagrams' | 'dfd_diagrams' | 'database_design'
  | 'planning' | 'estimation' | 'risks'
  | 'test_cases' | 'traceability' | 'metrics' | 'maintenance';

export const MODULE_LABELS: Record<string, string> = {
  requirements: 'Requirements Analysis',
  user_stories: 'User Stories',
  srs: 'SRS Document',
  uml_diagrams: 'UML Diagrams',
  dfd_diagrams: 'DFD Diagrams',
  database_design: 'Database Design',
  planning: 'Project Planning',
  estimation: 'Software Estimation',
  risks: 'Risk Management',
  test_cases: 'Test Cases',
  traceability: 'Traceability Matrix',
  metrics: 'Quality Metrics',
  maintenance: 'Maintenance Plan',
};

export const ALL_MODULES: GenerationModule[] = [
  'requirements', 'user_stories', 'srs',
  'uml_diagrams', 'dfd_diagrams', 'database_design',
  'planning', 'estimation', 'risks',
  'test_cases', 'traceability', 'metrics', 'maintenance',
];
