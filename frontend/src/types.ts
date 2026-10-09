export type StatusTone = 'success' | 'warning' | 'info' | 'purple'

export interface ProjectSummary {
  id: string
  title: string
  description: string
  status: string
  status_tone: StatusTone
  updated_label: string
  source_count: number
  model_count: number
}

export interface ProjectFile {
  id: number
  name: string
  metadata: string
  kind: 'source' | 'template' | 'form'
  status: string
  mime_type?: string | null
  byte_size?: number
  page_count: number
  chunk_count: number
}

export interface ProjectFileContent extends ProjectFile {
  content: string
}

export interface GlobalKnowledgeDocument {
  id: number
  name: string
  category: 'general' | 'company'
  metadata: string
  status: string
  mime_type: string
  byte_size: number
  page_count: number
  chunk_count: number
}

export interface GlobalKnowledgeDocumentContent extends GlobalKnowledgeDocument {
  content: string
}

export interface GlobalKnowledgeOverview {
  documents: GlobalKnowledgeDocument[]
  document_count: number
  chunk_count: number
}

export interface KnowledgeSource {
  id: number
  name: string
  detail: string
  scope: 'project' | 'global'
  tone: StatusTone
  item_count: number
}

export interface KnowledgeArtifactSummary {
  id: string
  kind: string
  scope: 'global' | 'project'
  title: string
  filename: string
  status: string
  byte_size: number
  version: number
  updated_at: string
  editable: boolean
  chunk_count: number
}

export interface KnowledgeArtifactDetail extends KnowledgeArtifactSummary {
  content: string
}

export interface DraftGenerationResult {
  available_fact_count: number
  artifact: KnowledgeArtifactDetail
  verified_fact_count: number
  used_fact_count: number
  missing_information: string[]
  model: string
  total_tokens: number | null
}

export type CompilationDownload = 'docx' | 'report' | 'template'

export interface DocumentCompilationSummary {
  id: string
  project_id: string
  template_name: string
  created_at: string
  status: 'needs_review'
  downloads: Record<CompilationDownload, string>
}

export interface CompilationField {
  cell_id: string
  label: string
  entity: 'company' | 'person' | 'project' | 'authority' | 'other'
  kind: 'data' | 'choice' | 'declaration' | 'signature'
  status: 'proposed' | 'missing' | 'needs_review' | 'not_applicable'
  value: string | null
  written_value: string | null
  reason: string
  validation_notes: string[]
  validation_codes?: string[]
  rejected_evidence?: { source_id: string; quote: string; reason: string }[]
  // Optional metadata in previously saved reports; new compilations use one request.
  repair?: {
    status: 'corrected' | 'unresolved'
    attempted: boolean
    message: string
    initial_proposal: {
      value: string | null
      validation_notes: string[]
      rejected_evidence: { source_id: string; quote: string; reason: string }[]
    }
  }
  location?: { kind: 'table_cell' } | { kind: 'paragraph'; paragraph: number; slot: number; placeholder: string }
  evidence: {
    source_id: string
    document_id: number | null
    source_name: string
    scope: 'company' | 'project' | 'general' | 'user'
    source_kind?: string
    origin?: 'document' | 'extracted' | 'user'
    fragment: number | null
    page: number | null
    quote: string
    content_sha256: string
  }[]
}

export interface DocumentCompilation extends DocumentCompilationSummary {
  report: {
    schema_version: number
    project_id: string
    created_at: string
    status: 'needs_review'
    ready_for_submission: false
    model: string
    prompt_version: string
    template_sha256: string
    output_sha256: string
    total_tokens: number | null
    instructions: string
    fields: CompilationField[]
    warnings: string[]
    unclassified_cells: string[]
    unclassified_fields?: string[]
    unsupported_locations?: { paragraph: number; reason: string }[]
    written_field_count: number
    blocked_field_count?: number
    unresolved_field_count: number
    source_coverage: {
      total_chunks: number
      selected_chunks: number
      total_characters: number
      selected_characters: number
      partial: boolean
      strategy: string
    }
  }
}

export interface Conversation {
  id: string
  title: string
  metadata: string
  target: string | null
}

export interface FormReference {
  form_id: number
  name: string
}

export type CompilationFieldStatus = 'PENDING' | 'RESOLVED' | 'MISSING' | 'AMBIGUOUS'
  | 'CONFLICTING' | 'NOT_APPLICABLE' | 'USER_PROVIDED'

export interface CompilationChatAction {
  session_id: string
  action: 'start' | 'updated' | 'clarify' | 'generated' | 'deferred' | 'paused' | 'resumed'
}

export interface CompilationChatState {
  enabled: boolean
  auto_continue: boolean
  paused: boolean
  paused_by_user?: boolean
  finish_requested?: boolean
  notice?: string | null
  deferred?: number
  question: { kind: 'value' | 'applicability' | 'clarifications' | 'generate' | 'deferred_summary'; field_ids: string[]; message: string } | null
  analyzed: number
  verified: number
  user_provided: number
  remaining_questions: number
  steps_used: number
  max_steps: number
  metrics?: { automatic_resolved: number; user_required_fields: number; user_turns: number }
}

export interface CompilationSessionSummary {
  id: string
  project_id: string
  conversation_id: string | null
  form_id: number | null
  original_file_id: number
  template_name: string
  status: 'CREATED' | 'ANALYZING' | 'WAITING_FOR_USER' | 'READY' | 'GENERATED' | 'FAILED'
  version: number
  created_at: string
  updated_at: string
  lease_until: string | null
  last_error: string | null
  summary: {
    total: number
    pending: number
    resolved: number
    missing: number
    ambiguous: number
    conflicting: number
    not_applicable: number
    user_provided: number
  }
  chat?: CompilationChatState
  last_generation: (DocumentCompilationSummary & { session_version: number }) | null
}

export interface CompilationSourceEvidence extends Evidence {
  role: 'source'
  quote: string
}

export interface CompilationSessionField {
  id: string
  candidate_id: string
  label: string
  value: string | null
  status: CompilationFieldStatus
  provenance: 'SOURCE' | 'USER' | 'FORM' | null
  reason: string
  validation_errors: string[]
  form_evidence: { role: 'form'; source_name: string; quote?: string; candidate_id: string }
  source_evidence: CompilationSourceEvidence[]
  alternatives: { value: string; evidence: CompilationSourceEvidence }[]
  requirement: { name: string; person_role: string; form_quote: string } | null
}

export interface CompilationSession extends CompilationSessionSummary {
  fields: CompilationSessionField[]
  open_issues: { field_id: string; status: CompilationFieldStatus; label: string;
    reason: string; validation_errors: string[] }[]
}

export interface CompilationFieldInput {
  field_id: string
  action: 'set' | 'not_applicable' | 'reset'
  value?: string
  reason?: string
}

export interface ProjectDetail extends ProjectSummary {
  instructions: string
  call_fact_count: number
  missing_fact_count: number
  files: ProjectFile[]
  knowledge_sources: KnowledgeSource[]
  conversations: Conversation[]
}

export interface DocumentField {
  id: number
  section: string
  label: string
  value: string | null
  provenance: string | null
  source_kind: 'company' | 'call' | 'project' | 'user'
  status: 'verified' | 'missing'
}

export interface DocumentReview {
  title: string
  subtitle: string
  completed_fields: number
  total_fields: number
  fields: DocumentField[]
}

export interface Evidence {
  chunk_id: number
  file_id: number
  source_name: string
  chunk_index: number
  excerpt: string
  relevance: number
  role?: 'form' | 'source'
  project_id?: string | null
  document_metadata?: string
  scope?: string | null
  category?: 'company' | 'general' | null
}

export interface EvidenceSearch {
  query: string
  results: Evidence[]
}

export type GenerationStatus =
  | 'completed'
  | 'direct'
  | 'not_configured'
  | 'no_evidence'
  | 'failed'

export interface GroundedAnswer {
  conversation_id: string
  turn_id: number
  question: string
  answer: string | null
  citations: number[]
  missing_information: string[]
  evidence: Evidence[]
  generation_status: GenerationStatus
  model: string | null
  total_tokens: number | null
  notice: string | null
  compilation?: CompilationChatAction | null
  form_reference?: FormReference | null
}

export interface ConversationTurnData {
  id: number
  question: string
  answer: string | null
  citations: number[]
  missing_information: string[]
  evidence: Evidence[]
  generation_status: GenerationStatus
  model: string | null
  total_tokens: number | null
  notice: string | null
  compilation?: CompilationChatAction | null
  form_reference?: FormReference | null
}

export interface ConversationDetail extends Conversation {
  project_id: string
  turns: ConversationTurnData[]
  compilation?: CompilationChatAction | null
  form_reference?: FormReference | null
}
export type AiProvider = 'openai' | 'anthropic' | 'google' | 'deepseek' | 'mistral'
  | 'xai' | 'groq' | 'openrouter' | 'ollama' | 'compatible'

export interface AiProviderDefinition {
  id: AiProvider
  name: string
  base_url: string
  credentials_url: string
  description: string
  requires_key: boolean
  browser_login: boolean
}

export interface AiLoginFlow {
  connection_token: string
  authorization_url: string
  expires_in: number
}

export interface AiProfile {
  id: string
  name: string
  provider: AiProvider
  base_url: string
  model: string
  context_window: number
  has_api_key: boolean
}

export interface AiProfileInput {
  name: string
  provider: AiProvider
  base_url: string
  model: string
  context_window: number
  api_key?: string
  connection_token?: string
  clear_api_key?: boolean
}

export interface AiSettings {
  profiles: AiProfile[]
  default_profile_id: string | null
  providers?: AiProviderDefinition[]
}

export interface ProjectAiSelection {
  profile_id: string | null
  effective_profile: AiProfile | null
}

export interface RetrievalConfig {
  backend: 'fts5' | 'qdrant'
  qdrant_mode: 'local' | 'remote'
  qdrant_url: string
  embedding_url: string
  embedding_model: string
  query_prefix: string
  document_prefix: string
}

export interface RetrievalSettings extends RetrievalConfig {
  has_qdrant_api_key: boolean
  has_embedding_api_key: boolean
}

export interface RetrievalInput extends RetrievalConfig {
  qdrant_api_key?: string
  embedding_api_key?: string
  clear_qdrant_api_key?: boolean
  clear_embedding_api_key?: boolean
}

export interface VectorIndexResult {
  collection: string
  indexed_chunks: number
  updated_chunks: number
  deleted_chunks: number
  dimensions: number
  embedding_digest: string
}
