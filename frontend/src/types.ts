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
}

export interface KnowledgeSource {
  id: number
  name: string
  detail: string
  scope: 'project' | 'global'
  tone: StatusTone
  item_count: number
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
