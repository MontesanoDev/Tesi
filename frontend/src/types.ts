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
  page_count: number
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
