import React, { useState } from 'react'
import { uploadDocument } from '../services/api'
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'
import './DocumentUpload.css'

const DocumentUpload = () => {
  const [file, setFile] = useState(null)
  const [documentType, setDocumentType] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0])
      setError(null)
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a file to upload')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await uploadDocument(file, documentType || null)
      setResult(data)
      setFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload document')
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
    <div className="document-upload">
      <div className="page-header">
        <h2>Document Upload & Analysis</h2>
        <p>Upload SAR, KYC documents, or transaction records for automated analysis</p>
      </div>

      <div className="upload-form-card">
        <form onSubmit={handleSubmit}>
          <div 
            className={`file-drop-zone ${dragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="file-preview">
                <FileText size={48} />
                <p className="file-name">{file.name}</p>
                <p className="file-size">{(file.size / 1024).toFixed(2)} KB</p>
                <button 
                  type="button" 
                  className="btn-remove"
                  onClick={() => setFile(null)}
                >
                  Remove
                </button>
              </div>
            ) : (
              <>
                <Upload size={48} />
                <p className="drop-text">Drag & drop your file here</p>
                <p className="drop-subtext">or</p>
                <label htmlFor="file-input" className="btn btn-secondary">
                  Browse Files
                </label>
                <input
                  id="file-input"
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.png,.jpg,.jpeg,.docx,.doc,.txt,.csv,.xlsx,.xls"
                  style={{ display: 'none' }}
                />
                <p className="supported-formats">
                  Supported: PDF, Images, Word, CSV, Excel
                </p>
              </>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="documentType">Document Type (Optional)</label>
            <select
              id="documentType"
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              className="form-select"
              disabled={loading}
            >
              <option value="">Auto-detect</option>
              <option value="SAR">Suspicious Activity Report (SAR)</option>
              <option value="TRANSACTION">Transaction Record</option>
              <option value="KYC">KYC Document</option>
            </select>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary btn-full"
            disabled={loading || !file}
          >
            {loading ? (
              <>
                <div className="btn-spinner"></div>
                Analyzing Document...
              </>
            ) : (
              <>
                <Upload size={20} />
                Upload & Analyze
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
            <h3>Analysis Results</h3>
            <span className="analysis-id">ID: {result.analysis_id}</span>
          </div>

          <div className="result-summary">
            <div className="summary-item">
              <label>Document Type</label>
              <p>{result.document_type}</p>
            </div>
            <div className="summary-item">
              <label>Processing Time</label>
              <p>{result.processing_time_ms}ms</p>
            </div>
            <div className="summary-item">
              <label>Timestamp</label>
              <p>{new Date(result.timestamp).toLocaleString()}</p>
            </div>
          </div>

          {result.extracted_data && (
            <div className="extracted-data-section">
              <h4>Extracted Data</h4>
              <div className="data-grid">
                {Object.entries(result.extracted_data).map(([key, value]) => (
                  <div key={key} className="data-item">
                    <label>{key.replace(/_/g, ' ').toUpperCase()}</label>
                    <p>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.risk_assessment && (
            <div className="risk-assessment-section">
              <h4>Risk Assessment</h4>
              <div className="risk-summary">
                <div className="risk-score-display" style={{ 
                  borderColor: getRiskColor(result.risk_assessment.risk_level) 
                }}>
                  <div className="score-value" style={{ 
                    color: getRiskColor(result.risk_assessment.risk_level) 
                  }}>
                    {result.risk_assessment.final_risk_score.toFixed(1)}
                  </div>
                  <div className="score-label">Risk Score</div>
                  <span className="risk-badge" style={{
                    background: getRiskColor(result.risk_assessment.risk_level) + '20',
                    color: getRiskColor(result.risk_assessment.risk_level)
                  }}>
                    {result.risk_assessment.risk_level}
                  </span>
                </div>

                <div className="risk-details">
                  <div className="risk-metric">
                    <span>Sanctions Risk</span>
                    <strong>{result.risk_assessment.sanctions_risk.toFixed(1)}%</strong>
                  </div>
                  <div className="risk-metric">
                    <span>PEP Risk</span>
                    <strong>{result.risk_assessment.pep_risk.toFixed(1)}%</strong>
                  </div>
                  <div className="risk-metric">
                    <span>Adverse Media</span>
                    <strong>{result.risk_assessment.adverse_media_risk.toFixed(1)}%</strong>
                  </div>
                  <div className="risk-metric">
                    <span>Behavioral Risk</span>
                    <strong>{result.risk_assessment.behavioral_risk.toFixed(1)}%</strong>
                  </div>
                </div>
              </div>

              {result.risk_assessment.flags && result.risk_assessment.flags.length > 0 && (
                <div className="flags-list">
                  <h5>Risk Flags</h5>
                  {result.risk_assessment.flags.map((flag, index) => (
                    <div key={index} className="flag-item">
                      <AlertCircle size={16} />
                      {flag}
                    </div>
                  ))}
                </div>
              )}

              {result.risk_assessment.recommendations && result.risk_assessment.recommendations.length > 0 && (
                <div className="recommendations-list">
                  <h5>Recommendations</h5>
                  {result.risk_assessment.recommendations.map((rec, index) => (
                    <div key={index} className="recommendation-item">
                      <CheckCircle size={16} />
                      {rec}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default DocumentUpload
