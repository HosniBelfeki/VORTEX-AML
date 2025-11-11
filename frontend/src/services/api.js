import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health Check
export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

// Dashboard Stats
export const getDashboardStats = async () => {
  const response = await api.get('/dashboard/stats')
  return response.data
}

// Manual Entity Screening
export const analyzeEntityManual = async (entityName, entityType = 'individual') => {
  const response = await api.post('/analyze/manual', {
    entity_name: entityName,
    entity_type: entityType,
  })
  return response.data
}

// Document Upload
export const uploadDocument = async (file, documentType = null) => {
  const formData = new FormData()
  formData.append('file', file)
  if (documentType) {
    formData.append('document_type', documentType)
  }

  const response = await api.post('/analyze/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// CSV Bulk Analysis
export const uploadCSVBulk = async (file, maxRows = 100) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('max_rows', maxRows)

  const response = await api.post('/analyze/csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Get Analysis by ID
export const getAnalysis = async (analysisId) => {
  const response = await api.get(`/analysis/${analysisId}`)
  return response.data
}

// List Analyses
export const listAnalyses = async (limit = 10, riskLevel = null) => {
  const params = { limit }
  if (riskLevel) {
    params.risk_level = riskLevel
  }
  const response = await api.get('/analyses', { params })
  return response.data
}

// Delete Analysis
export const deleteAnalysis = async (analysisId) => {
  const response = await api.delete(`/analysis/${analysisId}`)
  return response.data
}

// Generate SAR
export const generateSAR = async (analysisId) => {
  const response = await api.post(`/sars/generate?analysis_id=${analysisId}`)
  return response.data
}

// Get Compliance Cases
export const getComplianceCases = async (limit = 50, riskLevel = null) => {
  const params = { limit }
  if (riskLevel) {
    params.risk_level = riskLevel
  }
  const response = await api.get('/cases', { params })
  return response.data
}

// Assign Case
export const assignCase = async (caseId, assignedTo) => {
  const response = await api.post(`/cases/${caseId}/assign`, null, {
    params: { assigned_to: assignedTo }
  })
  return response.data
}

// Get Audit Trail
export const getAuditTrail = async (caseId) => {
  const response = await api.get(`/audit/${caseId}`)
  return response.data
}

// Generate Compliance Report
export const generateComplianceReport = async (startDate, endDate, format = 'json') => {
  const response = await api.post('/reports/compliance', null, {
    params: {
      start_date: startDate,
      end_date: endDate,
      format: format
    }
  })
  return response.data
}

export default api
