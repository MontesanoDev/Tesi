import { Navigate, Route, Routes } from 'react-router-dom'
import { CandidatureDemoPage } from './pages/CandidatureDemoPage'
import { CompanyKnowledgePage } from './pages/CompanyKnowledgePage'
import { DocumentReviewPage } from './pages/DocumentReviewPage'
import { GeneralSettingsPage } from './pages/GeneralSettingsPage'
import { KnowledgeArtifactsPage } from './pages/KnowledgeArtifactsPage'
import { ProjectWorkspacePage } from './pages/ProjectWorkspacePage'
import { ProjectsPage } from './pages/ProjectsPage'
import './App.css'

export default function App() {
  return (
    <Routes>
      <Route path="/demo/candidatura" element={<CandidatureDemoPage />} />
      <Route path="/" element={<Navigate to="/projects" replace />} />
      <Route path="/projects" element={<ProjectsPage />} />
      <Route path="/projects/:projectId" element={<ProjectWorkspacePage />} />
      <Route
        path="/projects/:projectId/conversations/:conversationId"
        element={<ProjectWorkspacePage />}
      />
      <Route
        path="/projects/:projectId/knowledge"
        element={<KnowledgeArtifactsPage />}
      />
      <Route
        path="/projects/:projectId/review"
        element={<DocumentReviewPage />}
      />
      <Route path="/settings" element={<GeneralSettingsPage />} />
      <Route path="/company-knowledge" element={<CompanyKnowledgePage />} />
      <Route path="*" element={<Navigate to="/projects" replace />} />
    </Routes>
  )
}
