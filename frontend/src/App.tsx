import { Navigate, Route, Routes } from 'react-router-dom'
import { DocumentReviewPage } from './pages/DocumentReviewPage'
import { GeneralSettingsPage } from './pages/GeneralSettingsPage'
import { ProjectSettingsPage } from './pages/ProjectSettingsPage'
import { ProjectWorkspacePage } from './pages/ProjectWorkspacePage'
import { ProjectsPage } from './pages/ProjectsPage'
import './App.css'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/projects" replace />} />
      <Route path="/projects" element={<ProjectsPage />} />
      <Route path="/projects/:projectId" element={<ProjectWorkspacePage />} />
      <Route
        path="/projects/:projectId/settings"
        element={<ProjectSettingsPage />}
      />
      <Route
        path="/projects/:projectId/review"
        element={<DocumentReviewPage />}
      />
      <Route path="/settings" element={<GeneralSettingsPage />} />
      <Route path="*" element={<Navigate to="/projects" replace />} />
    </Routes>
  )
}
