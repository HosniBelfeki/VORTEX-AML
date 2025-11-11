import React, { useState } from 'react'
import { generateComplianceReport } from '../services/api'
import { FileText, Download, Calendar } from 'lucide-react'
import './Reports.css'

const Reports = () => {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [format, setFormat] = useState('json')
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async (e) => {
    e.preventDefault()

    if (!startDate || !endDate) {
      setError('Please select both start and end dates')
      return
    }

    try {
      setLoading(true)
      setError(null)
      const data = await generateComplianceReport(startDate, endDate, format)
      setReport(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate report')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="reports-page">
      <div className="page-header">
        <div>
          <h2>Compliance Reports</h2>
          <p>Generate regulatory compliance reports for audits and submissions</p>
        </div>
      </div>

      <div className="report-form-card">
        <form onSubmit={handleGenerate}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="startDate">
                <Calendar size={16} />
                Start Date
              </label>
              <input
                type="date"
                id="startDate"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="form-input"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="endDate">
                <Calendar size={16} />
                End Date
              </label>
              <input
                type="date"
                id="endDate"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="form-input"
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="format">Report Format</label>
            <select
              id="format"
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="form-select"
              disabled={loading}
            >
              <option value="json">JSON</option>
              <option value="pdf">PDF</option>
            </select>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary btn-full"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="btn-spinner"></div>
                Generating Report...
              </>
            ) : (
              <>
                <FileText size={20} />
                Generate Report
              </>
            )}
          </button>
        </form>
      </div>

      {error && (
        <div className="alert alert-error">{error}</div>
      )}

      {report && (
        <div className="report-result-card">
          <div className="report-header">
            <div>
              <h3>Compliance Report</h3>
              <p className="report-id">Report ID: {report.report_id}</p>
            </div>
            <button className="btn btn-secondary">
              <Download size={18} />
              Download
            </button>
          </div>

          <div className="report-meta">
            <div className="meta-item">
              <label>Period</label>
              <p>{report.period}</p>
            </div>
            <div className="meta-item">
              <label>Generated At</label>
              <p>{new Date(report.generated_at).toLocaleString()}</p>
            </div>
          </div>

          {report.summary && (
            <div className="report-section">
              <h4>Summary Statistics</h4>
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-value">{report.summary.total_cases}</div>
                  <div className="stat-label">Total Cases</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{report.summary.high_risk_cases}</div>
                  <div className="stat-label">High Risk</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{report.summary.critical_cases}</div>
                  <div className="stat-label">Critical</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{report.summary.sars_filed}</div>
                  <div className="stat-label">SARs Filed</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{report.summary.false_positives}</div>
                  <div className="stat-label">False Positives</div>
                </div>
              </div>
            </div>
          )}

          {report.regulatory_compliance && (
            <div className="report-section">
              <h4>Regulatory Compliance Status</h4>
              <div className="compliance-grid">
                {Object.entries(report.regulatory_compliance).map(([key, value]) => (
                  <div key={key} className="compliance-item">
                    <div className="compliance-name">
                      {key.replace(/_/g, ' ').toUpperCase()}
                    </div>
                    <div className={`compliance-status ${value.toLowerCase()}`}>
                      {value}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {format === 'json' && (
            <div className="report-section">
              <h4>Full Report Data</h4>
              <pre className="report-json">
                {JSON.stringify(report, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      <div className="report-templates">
        <h3>Available Report Templates</h3>
        <div className="templates-grid">
          <div className="template-card">
            <FileText size={32} />
            <h4>Monthly Compliance Report</h4>
            <p>Comprehensive monthly AML compliance summary</p>
          </div>
          <div className="template-card">
            <FileText size={32} />
            <h4>SAR Filing Report</h4>
            <p>Summary of all Suspicious Activity Reports filed</p>
          </div>
          <div className="template-card">
            <FileText size={32} />
            <h4>Risk Assessment Report</h4>
            <p>Detailed risk analysis and trends</p>
          </div>
          <div className="template-card">
            <FileText size={32} />
            <h4>Audit Trail Report</h4>
            <p>Complete audit log for regulatory review</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Reports
