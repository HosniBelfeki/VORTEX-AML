import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ManualScreening from './pages/ManualScreening'
import DocumentUpload from './pages/DocumentUpload'
import BulkAnalysis from './pages/BulkAnalysis'
import AnalysesList from './pages/AnalysesList'
import AnalysisDetail from './pages/AnalysisDetail'
import Cases from './pages/Cases'
import Reports from './pages/Reports'
import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/screening" element={<ManualScreening />} />
          <Route path="/upload" element={<DocumentUpload />} />
          <Route path="/bulk" element={<BulkAnalysis />} />
          <Route path="/analyses" element={<AnalysesList />} />
          <Route path="/analysis/:id" element={<AnalysisDetail />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
