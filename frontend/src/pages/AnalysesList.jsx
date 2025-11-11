import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { listAnalyses } from '../services/api'
import { Filter, RefreshCw } from 'lucide-react'
import './AnalysesList.css'

const AnalysesList = () => {
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [riskFilter, setRiskFilter] = useState('')
  const [limit, setLimit] = useState(50)

  useEffect(() => {
    loadAnalyses()
  }, [riskFilter, limit])

  const loadAnalyses = async () => {
    try {
      setLoading(true)
      const data = await listAnalyses(limit, riskFilter || null)
      setAnalyses(Array.isArray(data) ? data : [])
      setError(null)
    } catch (err) {
      setError('Failed to load analyses')
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

  return (
    <div className="analyses-list">
      <div className="page-header">
        <h2>All Analyses</h2>
        <button onClick={loadAnalyses} className="btn btn-secondary" disabled={loading}>
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

        <div className="filter-group">
          <label>Show:</label>
          <select
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
            className="filter-select"
          >
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      ) : error ? (
        <div className="alert alert-error">{error}</div>
      ) : analyses.length === 0 ? (
        <div className="empty-state">
          <p>No analyses found</p>
        </div>
      ) : (
        <div className="analyses-table-card">
          <table className="analyses-table">
            <thead>
              <tr>
                <th>Analysis ID</th>
                <th>Entity/Type</th>
                <th>Risk Level</th>
                <th>Risk Score</th>
                <th>Timestamp</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {analyses.map((analysis) => {
                const riskLevel = analysis.risk_level || analysis.risk_assessment?.risk_level
                const riskScore = analysis.risk_score || analysis.risk_assessment?.final_risk_score || 0
                const entityName = analysis.entity_name || analysis.document_type || 'Document'

                return (
                  <tr key={analysis.analysis_id}>
                    <td>
                      <code className="analysis-id">{analysis.analysis_id}</code>
                    </td>
                    <td>
                      <div className="entity-info">
                        <strong>{entityName}</strong>
                        {analysis.entity_type && (
                          <span className="entity-type">{analysis.entity_type}</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span 
                        className="risk-badge"
                        style={{
                          background: getRiskColor(riskLevel) + '20',
                          color: getRiskColor(riskLevel)
                        }}
                      >
                        {riskLevel}
                      </span>
                    </td>
                    <td>
                      <strong>{riskScore.toFixed(1)}</strong>
                    </td>
                    <td>{new Date(analysis.timestamp).toLocaleString()}</td>
                    <td>
                      <Link 
                        to={`/analysis/${analysis.analysis_id}`}
                        className="btn-view"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default AnalysesList
