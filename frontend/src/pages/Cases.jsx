import React, { useState, useEffect } from 'react'
import { getComplianceCases } from '../services/api'
import { Briefcase, Filter, RefreshCw } from 'lucide-react'
import './Cases.css'

const Cases = () => {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [riskFilter, setRiskFilter] = useState('')

  useEffect(() => {
    loadCases()
  }, [riskFilter])

  const loadCases = async () => {
    try {
      setLoading(true)
      const data = await getComplianceCases(50, riskFilter || null)
      setCases(data.cases || [])
      setError(null)
    } catch (err) {
      setError('Failed to load compliance cases')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level) => {
    const colors = {
      LOW: '#10b981',
      MEDIUM: '#f59e0b',
      HIGH: '#f97316',
      CRITICAL: '#ef4444'
    }
    return colors[level] || '#6b7280'
  }

  const getStatusColor = (status) => {
    const colors = {
      pending_review: '#f59e0b',
      under_investigation: '#3b82f6',
      resolved: '#10b981',
      escalated: '#ef4444'
    }
    return colors[status] || '#6b7280'
  }

  return (
    <div className="cases-page">
      <div className="page-header">
        <div>
          <h2>Compliance Cases</h2>
          <p>Manage and track AML compliance cases</p>
        </div>
        <button onClick={loadCases} className="btn btn-secondary" disabled={loading}>
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      <div className="filters-bar">
        <div className="filter-group">
          <Filter size={18} />
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      ) : error ? (
        <div className="alert alert-error">{error}</div>
      ) : cases.length === 0 ? (
        <div className="empty-state">
          <Briefcase size={64} />
          <h3>No Cases Found</h3>
          <p>Start analyzing documents to create compliance cases</p>
        </div>
      ) : (
        <div className="cases-grid">
          {cases.map((caseItem) => (
            <div key={caseItem.case_id} className="case-card">
              <div className="case-header">
                <div className="case-id">
                  <Briefcase size={18} />
                  <code>{caseItem.case_id}</code>
                </div>
                <span 
                  className="status-badge"
                  style={{
                    background: getStatusColor(caseItem.status) + '20',
                    color: getStatusColor(caseItem.status)
                  }}
                >
                  {caseItem.status.replace(/_/g, ' ')}
                </span>
              </div>

              <div className="case-body">
                <div className="case-info">
                  <label>Entity Name</label>
                  <p>{caseItem.entity_name}</p>
                </div>

                <div className="case-info">
                  <label>Entity Type</label>
                  <p className="capitalize">{caseItem.entity_type}</p>
                </div>

                <div className="case-risk">
                  <div className="risk-score-mini">
                    <span 
                      className="score"
                      style={{ color: getRiskColor(caseItem.risk_level) }}
                    >
                      {caseItem.risk_score.toFixed(1)}
                    </span>
                    <span 
                      className="level"
                      style={{
                        background: getRiskColor(caseItem.risk_level) + '20',
                        color: getRiskColor(caseItem.risk_level)
                      }}
                    >
                      {caseItem.risk_level}
                    </span>
                  </div>
                </div>

                <div className="case-info">
                  <label>Created</label>
                  <p>{new Date(caseItem.created_at).toLocaleDateString()}</p>
                </div>

                {caseItem.assigned_to && (
                  <div className="case-info">
                    <label>Assigned To</label>
                    <p>{caseItem.assigned_to}</p>
                  </div>
                )}
              </div>

              <div className="case-footer">
                <button className="btn-case-action">View Details</button>
                <button className="btn-case-action secondary">Assign</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Cases
