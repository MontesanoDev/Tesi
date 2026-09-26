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
  kind: 'source' | 'template'
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

export interface ProjectGlobalKnowledgeDocument extends GlobalKnowledgeDocument {
  linked: boolean
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

export interface CallFactsExtractionResult {
  artifact: KnowledgeArtifactDetail
  fact_count: number
  missing_count: number
  evidence_count: number
  model: string
  total_tokens: number | null
}

export type CallFactStatus = 'pending' | 'verified' | 'discarded'
export type CallFactAction = 'verify' | 'edit' | 'discard' | 'restore'

export interface CallFactSource {
  name: string
  fragment: number
}

export interface CallFactItem {
  id: string
  title: string
  value: string
  status: CallFactStatus
  sources: CallFactSource[]
  origin?: 'extracted' | 'user_corrected'
}

export interface CallFactsReview {
  artifact: KnowledgeArtifactDetail
  facts: CallFactItem[]
  missing_information: string[]
  pending_count: number
  verified_count: number
  discarded_count: number
}

export interface CallFactRevision {
  action: CallFactAction
  version: number
  title?: string
  value?: string
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
}

export interface ConversationDetail extends Conversation {
  project_id: string
  turns: ConversationTurnData[]
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
