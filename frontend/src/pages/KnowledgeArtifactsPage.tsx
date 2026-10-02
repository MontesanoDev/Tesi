import { Navigate, useParams, useSearchParams } from 'react-router-dom'

// Keep bookmarks to the former standalone workspace working.
export function KnowledgeArtifactsPage() {
  const { projectId } = useParams()
  const [params] = useSearchParams()
  const format = params.get('artifact') === 'output_draft' ? 'text' : 'docx'
  return <Navigate to={`/projects/${projectId}?documents=${format}`} replace />
}
