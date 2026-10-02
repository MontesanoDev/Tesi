import { Navigate, useParams } from 'react-router-dom'

// Keep bookmarks to the former standalone workspace working.
export function KnowledgeArtifactsPage() {
  const { projectId } = useParams()
  return <Navigate to={`/projects/${projectId}`} replace />
}
