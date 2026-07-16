/** TypeScript interfaces mirroring backend Pydantic models. */

// ── Meta ────────────────────────────────────────────────────────────────

export interface StepTrace {
  step: string;
  latency_ms: number;
  tokens: number;
  estimated_cost_usd: number;
  success: boolean;
}

export interface StepMeta {
  request_id: string;
  steps: StepTrace[];
  total_latency_ms: number;
  total_tokens: number;
  estimated_cost_usd: number;
}

// ── Intake ──────────────────────────────────────────────────────────────

export interface IntakeData {
  product_name: string;
  problem_statement: string;
  context: string;
}

export interface ClarifyingQuestion {
  id: string;
  question: string;
  rationale: string;
  example_answer: string;
}

export interface IntakeResponse {
  questions: ClarifyingQuestion[];
  meta: StepMeta;
}

// ── Generate ────────────────────────────────────────────────────────────

export interface QuestionAnswer {
  question_id: string;
  question: string;
  answer: string;
}

export interface GenerateRequest {
  intake: IntakeData;
  answers: QuestionAnswer[];
}

// ── PRD ─────────────────────────────────────────────────────────────────

export interface FunctionalRequirement {
  id: string;
  title: string;
  description: string;
  acceptance_criteria: string[];
  priority: string;
}

export interface NonFunctionalRequirement {
  id: string;
  category: string;
  description: string;
  metric: string;
}

export interface UserFlow {
  name: string;
  steps: string[];
  error_scenarios: string[];
}

export interface Risk {
  description: string;
  severity: string;
  mitigation: string;
}

export interface PRDDocument {
  title: string;
  summary: string;
  problem_statement: string;
  target_users: string[];
  goals: string[];
  non_goals: string[];
  assumptions: string[];
  functional_requirements: FunctionalRequirement[];
  non_functional_requirements: NonFunctionalRequirement[];
  user_flows: UserFlow[];
  success_metrics: string[];
  risks: Risk[];
  open_questions: string[];
  dependencies: string[];
  release_considerations: string[];
}

// ── Critic ──────────────────────────────────────────────────────────────

export interface CriticIssue {
  category: string;
  severity: string;
  location: string;
  suggestion: string;
}

export interface CriticEvaluation {
  quality_score: number;
  confidence_score: number;
  issues: CriticIssue[];
  recommendations: string[];
  readiness: string;
}

// ── Generate response ───────────────────────────────────────────────────

export interface GenerateResponse {
  prd: PRDDocument;
  evaluation: CriticEvaluation;
  revision_applied: boolean;
  prd_markdown: string;
  meta: StepMeta;
}

// ── Tickets ─────────────────────────────────────────────────────────────

export interface AcceptanceCriterion {
  given: string;
  when: string;
  then: string;
}

export interface Story {
  id: string;
  title: string;
  description: string;
  acceptance_criteria: AcceptanceCriterion[];
  story_points: number;
}

export interface Epic {
  id: string;
  title: string;
  description: string;
  stories: Story[];
}

export interface TicketsResponse {
  epics: Epic[];
  total_story_count: number;
  meta: StepMeta;
}

// ── Workflow state ──────────────────────────────────────────────────────

export type WorkflowStep = "intake" | "clarify" | "generate" | "review" | "tickets";

export type GenerationSubstep = "researching" | "writing" | "evaluating" | "revising" | "done";

export interface WorkflowState {
  step: WorkflowStep;
  intake: IntakeData | null;
  questions: ClarifyingQuestion[];
  answers: QuestionAnswer[];
  generateResult: GenerateResponse | null;
  ticketsResult: TicketsResponse | null;
  generationSubstep: GenerationSubstep;
  loading: boolean;
  error: string | null;
}

// ── FAQ (Agentic RAG) ───────────────────────────────────────────────────

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export interface FAQRequest {
  question: string;
  history: ChatTurn[];
}

export interface Citation {
  n: number;
  kind: "corpus" | "web";
  title: string;
  source: string;
  heading?: string;
  score?: number;
  snippet?: string;
}

export interface FAQResponse {
  answer: string;
  citations: Citation[];
  used_web: boolean;
  route_reason?: string;
  meta: StepMeta;
}

// ── History ─────────────────────────────────────────────────────────────

export interface HistoryEntry {
  id: string;
  intake: IntakeData;
  answers: QuestionAnswer[];
  prd: PRDDocument;
  prd_markdown: string;
  evaluation: CriticEvaluation;
  tickets: TicketsResponse | null;
  timestamp: number;
}
