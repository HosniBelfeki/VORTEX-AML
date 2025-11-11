import React, { useState } from 'react'
import { uploadCSVBulk } from '../services/api'
import { Upload, FileSpreadsheet, AlertCircle } from 'lucide-react'
import './BulkAnalysis.css'

const BulkAnalysis = () => {
  const [file, setFile] = useState(null)
  const [maxRows, setMaxRows] = useState(100)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile)
        setError(null)
      } else {
        setError('Please select a CSV file')
      }
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a CSV file')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await uploadCSVBulk(file, maxRows)
      setResult(data)
      setFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process CSV file')
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
      CRITICAL: '#ef4444',
      ERROR: '#6b7280'
    }
    return colors[level] || '#6b7280'
  }

  return (
    <div className="bulk-analysis">
      <div className="page-header">
        <h2>Bulk CSV Analysis</h2>
        <p>Upload CSV files with multiple transactions for batch screening</p>
      </div>

      <div className="upload-form-card">
        <form onSubmit={handleSubmit}>
          <div className="file-input-group">
            <label htmlFor="csv-file" className="file-label">
              <FileSpreadsheet size={24} />
              {file ? file.name : 'Choose CSV File'}
            </label>
            <input
              id="csv-file"
              type="file"
              onChange={handleFileChange}
              accept=".csv"
              style={{ display: 'none' }}
            />
          </div>

          <div className="form-group">
            <label htmlFor="maxRows">Maximum Rows to Process</label>
            <input
              type="number"
              id="maxRows"
              value={maxRows}
              onChange={(e) => setMaxRows(parseInt(e.target.value))}
              min="1"
              max="1000"
              className="form-input"
              disabled={loading}
            />
            <p className="help-text">Limit: 1-1000 rows</p>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary btn-full"
            disabled={loading || !file}
          >
            {loading ? (
              <>
                <div className="btn-spinner"></div>
                Processing CSV...
              </>
            ) : (
              <>
                <Upload size={20} />
                Process CSV
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
            <h3>Bulk Analysis Results</h3>
            <span className="analysis-id">ID: {result.analysis_id}</span>
          </div>

          <div className="summary-stats">
            <div className="stat-box">
              <div className="stat-value">{result.total_rows}</div>
              <div className="stat-label">Total Rows</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{result.processed_rows}</div>
              <div className="stat-label">Processed</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{result.high_risk_count}</div>
              <div className="stat-label">High Risk</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{result.processing_time_ms}ms</div>
              <div className="stat-label">Processing Time</div>
            </div>
          </div>

          {result.summary && (
            <div className="risk-distribution">
              <h4>Risk Distribution</h4>
              <div className="distribution-grid">
                <div className="dist-item" style={{ borderColor: '#10b981' }}>
                  <div className="dist-count">{result.summary.low_risk}</div>
                  <div className="dist-label">Low Risk</div>
                </div>
                <div className="dist-item" style={{ borderColor: '#f59e0b' }}>
                  <div className="dist-count">{result.summary.medium_risk}</div>
                  <div className="dist-label">Medium Risk</div>
                </div>
                <div className="dist-item" style={{ borderColor: '#f97316' }}>
                  <div className="dist-count">{result.summary.high_risk}</div>
                  <div className="dist-label">High Risk</div>
                </div>
                <div className="dist-item" style={{ borderColor: '#ef4444' }}>
                  <div className="dist-count">{result.summary.critical_risk}</div>
                  <div className="dist-label">Critical</div>
                </div>
              </div>
            </div>
          )}

          {result.results && result.results.length > 0 && (
            <div className="results-table">
              <h4>Detailed Results</h4>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Row</th>
                      <th>Entity Name</th>
                      <th>Amount</th>
                      <th>Risk Level</th>
                      <th>Risk Score</th>
                      <th>Flags</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.results.map((row, index) => (
                      <tr key={index}>
                        <td>{row.row_number}</td>
                        <td>{row.entity_name}</td>
                        <td>${row.amount?.toLocaleString() || 0}</td>
                        <td>
                          <span 
                            className="risk-badge"
                            style={{
                              background: getRiskColor(row.risk_level) + '20',
                              color: getRiskColor(row.risk_level)
                            }}
                          >
                            {row.risk_level}
                          </span>
                        </td>
                        <td>{row.risk_score.toFixed(1)}</td>
                        <td>
                          {row.flags && row.flags.length > 0 ? (
                            <span className="flags-count">{row.flags.length} flags</span>
                          ) : (
                            <span className="no-flags">None</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default BulkAnalysis
