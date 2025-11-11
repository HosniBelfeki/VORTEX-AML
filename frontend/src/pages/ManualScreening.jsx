import React, { useState } from 'react'
import { analyzeEntityManual } from '../services/api'
import { Search, AlertCircle, CheckCircle } from 'lucide-react'
import './ManualScreening.css'

const ManualScreening = () => {
  const [entityName, setEntityName] = useState('')
  const [entityType, setEntityType] = useState('individual')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!entityName.trim()) {
      setError('Please enter an entity name')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await analyzeEntityManual(entityName, entityType)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze entity')
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
    <div className="manual-screening">
      <div className="page-header">
        <h2>Manual Entity Screening</h2>
        <p>Screen individuals or organizations against sanctions lists, PEP databases, and adverse media</p>
      </div>

      <div className="screening-form-card">
        <form onSubmit={handleSubmit} className="screening-form">
          <div className="form-group">
            <label htmlFor="entityName">Entity Name *</label>
            <input
              type="text"
              id="entityName"
              value={entityName}
              onChange={(e) => setEntityName(e.target.value)}
              placeholder="e.g., John Smith, ABC Corporation"
              className="form-input"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="entityType">Entity Type</label>
            <select
              id="entityType"
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
              className="form-select"
              disabled={loading}
            >
              <option value="individual">Individual</option>
              <option value="organization">Organization</option>
            </select>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="btn-spinner"></div>
                Analyzing...
              </>
            ) : (
              <>
                <Search size={20} />
                Screen Entity
              </>
            )}
          </button>
        </form>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {result && (
        <div className="result-card">
          <div className="result-header">
            <h3>Screening Results</h3>
            <span className="analysis-id">ID: {result.analysis_id}</span>
          </div>

          <div className="result-summary">
            <div className="summary-item">
              <label>Entity Name</label>
              <p>{result.entity_name}</p>
            </div>
            <div className="summary-item">
              <label>Entity Type</label>
              <p className="capitalize">{result.entity_type}</p>
            </div>
            <div className="summary-item">
              <label>Processing Time</label>
              <p>{result.processing_time_ms}ms</p>
            </div>
          </div>

          <div className="risk-overview">
            <div className="risk-score-card" style={{ borderColor: getRiskColor(result.risk_level) }}>
              <div className="risk-score-value" style={{ color: getRiskColor(result.risk_level) }}>
                {result.risk_score.toFixed(1)}
              </div>
              <div className="risk-score-label">Risk Score</div>
              <div className="risk-level-badge" style={{ 
                background: getRiskColor(result.risk_level) + '20',
                color: getRiskColor(result.risk_level)
              }}>
                {result.risk_level}
              </div>
            </div>

            <div className="risk-breakdown">
              <h4>Risk Breakdown</h4>
              <div className="risk-item">
                <span>Sanctions Risk</span>
                <div className="risk-bar">
                  <div 
                    className="risk-bar-fill" 
                    style={{ width: `${result.sanctions_risk}%`, background: '#ef4444' }}
                  ></div>
                </div>
                <span className="risk-value">{result.sanctions_risk.toFixed(1)}%</span>
              </div>
              <div className="risk-item">
                <span>PEP Risk</span>
                <div className="risk-bar">
                  <div 
                    className="risk-bar-fill" 
                    style={{ width: `${result.pep_risk}%`, background: '#f59e0b' }}
                  ></div>
                </div>
                <span className="risk-value">{result.pep_risk.toFixed(1)}%</span>
              </div>
              <div className="risk-item">
                <span>Adverse Media Risk</span>
                <div className="risk-bar">
                  <div 
                    className="risk-bar-fill" 
                    style={{ width: `${result.adverse_media_risk}%`, background: '#f97316' }}
                  ></div>
                </div>
                <span className="risk-value">{result.adverse_media_risk.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          {result.flags && result.flags.length > 0 && (
            <div className="flags-section">
              <h4>Risk Flags</h4>
              <div className="flags-list">
                {result.flags.map((flag, index) => (
                  <div key={index} className="flag-item">
                    <AlertCircle size={16} />
                    {flag}
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.recommendations && result.recommendations.length > 0 && (
            <div className="recommendations-section">
              <h4>Recommendations</h4>
              <div className="recommendations-list">
                {result.recommendations.map((rec, index) => (
                  <div key={index} className="recommendation-item">
                    <CheckCircle size={16} />
                    {rec}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ManualScreening
