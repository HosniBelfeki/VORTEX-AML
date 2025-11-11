import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getAnalysis, generateSAR } from '../services/api'
import { ArrowLeft, Download, FileText } from 'lucide-react'
import './AnalysisDetail.css'

const AnalysisDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sarData, setSarData] = useState(null)
  const [generatingSAR, setGeneratingSAR] = useState(false)

  useEffect(() => {
    loadAnalysis()
  }, [id])

  const loadAnalysis = async () => {
    try {
      setLoading(true)
      const data = await getAnalysis(id)
      setAnalysis(data)
      setError(null)
    } catch (err) {
      setError('Analysis not found')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateSAR = async () => {
    try {
      setGeneratingSAR(true)
      const data = await generateSAR(id)
      setSarData(data)
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to generate SAR')
    } finally {
      setGeneratingSAR(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="error-page">
        <h2>{error || 'Analysis not found'}</h2>
        <button onClick={() => navigate('/analyses')} className="btn btn-primary">
          Back to Analyses
        </button>
      </div>
    )
  }

  const riskLevel = analysis.risk_level || analysis.risk_assessment?.risk_level
  const riskScore = analysis.risk_score || analysis.risk_assessment?.final_risk_score || 0

  return (
    <div className="analysis-detail">
      <button onClick={() => navigate(-1)} className="btn-back">
        <ArrowLeft size={20} />
        Back
      </button>

      <div className="detail-header">
        <div>
          <h2>Analysis Details</h2>
          <code className="analysis-id">{analysis.analysis_id}</code>
        </div>
        {riskLevel === 'CRITICAL' && (
          <button 
            onClick={handleGenerateSAR}
            className="btn btn-danger"
            disabled={generatingSAR}
          >
            <FileText size={20} />
            {generatingSAR ? 'Generating...' : 'Generate SAR'}
          </button>
        )}
      </div>

      <div className="detail-grid">
        <div className="detail-card">
          <h3>Overview</h3>
          <div className="detail-item">
            <label>Entity Name</label>
            <p>{analysis.entity_name || 'Document Analysis'}</p>
          </div>
          {analysis.entity_type && (
            <div className="detail-item">
              <label>Entity Type</label>
              <p className="capitalize">{analysis.entity_type}</p>
            </div>
          )}
          {analysis.document_type && (
            <div className="detail-item">
              <label>Document Type</label>
              <p>{analysis.document_type}</p>
            </div>
          )}
          <div className="detail-item">
            <label>Timestamp</label>
            <p>{new Date(analysis.timestamp).toLocaleString()}</p>
          </div>
          {analysis.processing_time_ms && (
            <div className="detail-item">
              <label>Processing Time</label>
              <p>{analysis.processing_time_ms}ms</p>
            </div>
          )}
        </div>

        <div className="detail-card risk-card">
          <h3>Risk Assessment</h3>
          <div className="risk-score-large">
            <div className="score-value">{riskScore.toFixed(1)}</div>
            <div className="score-label">Risk Score</div>
            <span className={`risk-badge-large risk-${riskLevel?.toLowerCase()}`}>
              {riskLevel}
            </span>
          </div>
        </div>
      </div>

      {(analysis.risk_assessment || analysis.sanctions_risk !== undefined) && (
        <div className="detail-card">
          <h3>Risk Breakdown</h3>
          <div className="risk-metrics">
            <div className="metric">
              <label>Sanctions Risk</label>
              <div className="metric-bar">
                <div 
                  className="metric-fill" 
                  style={{ 
                    width: `${analysis.sanctions_risk || analysis.risk_assessment?.sanctions_risk || 0}%`,
                    background: '#ef4444'
                  }}
                ></div>
              </div>
              <span>{(analysis.sanctions_risk || analysis.risk_assessment?.sanctions_risk || 0).toFixed(1)}%</span>
            </div>
            <div className="metric">
              <label>PEP Risk</label>
              <div className="metric-bar">
                <div 
                  className="metric-fill" 
                  style={{ 
                    width: `${analysis.pep_risk || analysis.risk_assessment?.pep_risk || 0}%`,
                    background: '#f59e0b'
                  }}
                ></div>
              </div>
              <span>{(analysis.pep_risk || analysis.risk_assessment?.pep_risk || 0).toFixed(1)}%</span>
            </div>
            <div className="metric">
              <label>Adverse Media Risk</label>
              <div className="metric-bar">
                <div 
                  className="metric-fill" 
                  style={{ 
                    width: `${analysis.adverse_media_risk || analysis.risk_assessment?.adverse_media_risk || 0}%`,
                    background: '#f97316'
                  }}
                ></div>
              </div>
              <span>{(analysis.adverse_media_risk || analysis.risk_assessment?.adverse_media_risk || 0).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}

      {analysis.extracted_data && (
        <div className="detail-card">
          <h3>Extracted Data</h3>
          <div className="extracted-grid">
            {Object.entries(analysis.extracted_data).map(([key, value]) => (
              <div key={key} className="extracted-item">
                <label>{key.replace(/_/g, ' ').toUpperCase()}</label>
                <p>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {(analysis.flags || analysis.risk_assessment?.flags) && (
        <div className="detail-card">
          <h3>Risk Flags</h3>
          <div className="flags-grid">
            {(analysis.flags || analysis.risk_assessment?.flags || []).map((flag, index) => (
              <div key={index} className="flag-badge">
                {flag}
              </div>
            ))}
          </div>
        </div>
      )}

      {(analysis.recommendations || analysis.risk_assessment?.recommendations) && (
        <div className="detail-card">
          <h3>Recommendations</h3>
          <ul className="recommendations-list">
            {(analysis.recommendations || analysis.risk_assessment?.recommendations || []).map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {sarData && (
        <div className="detail-card sar-card">
          <div className="sar-header">
            <h3>Generated SAR Filing</h3>
            <button className="btn btn-secondary">
              <Download size={18} />
              Download
            </button>
          </div>
          <pre className="sar-content">{sarData.sar_filing}</pre>
        </div>
      )}
    </div>
  )
}

export default AnalysisDetail
