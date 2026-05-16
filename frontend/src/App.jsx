import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import AnalyzingPage from './pages/AnalyzingPage'
import DashboardPage from './pages/DashboardPage'
import GuidePage from './pages/GuidePage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/analyzing" element={<AnalyzingPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/guide" element={<GuidePage />} />
    </Routes>
  )
}
