import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getDashboardStats } from '../services/api'
import { 
  TrendingUp, 
  AlertTriangle, 
  AlertCircle, 
  Activity,
  ArrowRight 
} from 'lucide-react'
import './Dashboard.css'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const data = await getDashboardStats()
      setStats(data)
      setError(null)
    } catch (err) {
      setError('Failed to load dashboard statistics')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  if (error) {
    return <div className="error-message">{error}</div>
  }

  const recentAnalyses = stats?.analyses 
    ? Object.values(stats.analyses).slice(0, 5)
    : []

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Welcome to VORTEX-AML</h2>
        <p>Real-time Anti-Money Laundering Intelligence Platform</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dbeafe' }}>
            <Activity size={24} color="#2563eb" />
          </div>
          <div className="stat-content">
            <h3>{stats?.total_analyses || 0}</h3>
            <p>Total Analyses</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fef3c7' }}>
            <AlertTriangle size={24} color="#f59e0b" />
          </div>
          <div className="stat-content">
            <h3>{stats?.high_risk_count || 0}</h3>
            <p>High Risk Cases</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#fee2e2' }}>
            <AlertCircle size={24} color="#ef4444" />
          </div>
          <div className="stat-content">
            <h3>{stats?.critical_count || 0}</h3>
            <p>Critical Cases</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#dcfce7' }}>
            <TrendingUp size={24} color="#10b981" />
          </div>
          <div className="stat-content">
            <h3>{stats?.average_risk_score?.toFixed(1) || '0.0'}</h3>
            <p>Avg Risk Score</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="actions-grid">
          <Link to="/screening" className="action-card">
            <div className="action-icon">🔍</div>
            <h4>Manual Screening</h4>
            <p>Screen an entity by name</p>
            <ArrowRight size={20} />
          </Link>

          <Link to="/upload" className="action-card">
            <div className="action-icon">📄</div>
            <h4>Upload Document</h4>
            <p>Analyze SAR, KYC, or transaction</p>
            <ArrowRight size={20} />
          </Link>

          <Link to="/bulk" className="action-card">
            <div className="action-icon">📊</div>
            <h4>Bulk Analysis</h4>
            <p>Process CSV with multiple records</p>
            <ArrowRight size={20} />
          </Link>

          <Link to="/cases" className="action-card">
            <div className="action-icon">💼</div>
            <h4>View Cases</h4>
            <p>Manage compliance cases</p>
            <ArrowRight size={20} />
          </Link>
        </div>
      </div>

      {/* Recent Analyses */}
      {recentAnalyses.length > 0 && (
        <div className="recent-analyses">
          <div className="section-header">
            <h3>Recent Analyses</h3>
            <Link to="/analyses" className="view-all">View All</Link>
          </div>

          <div className="analyses-table">
            <table>
              <thead>
                <tr>
                  <th>Analysis ID</th>
                  <th>Entity</th>
                  <th>Risk Level</th>
                  <th>Risk Score</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {recentAnalyses.map((analysis) => {
                  const riskLevel = analysis.risk_level || analysis.risk_assessment?.risk_level
                  const riskScore = analysis.risk_score || analysis.risk_assessment?.final_risk_score || 0
                  const entityName = analysis.entity_name || 'Document Analysis'

                  return (
                    <tr key={analysis.analysis_id}>
                      <td>
                        <Link to={`/analysis/${analysis.analysis_id}`} className="analysis-link">
                          {analysis.analysis_id}
                        </Link>
                      </td>
                      <td>{entityName}</td>
                      <td>
                        <span className={`risk-badge risk-${riskLevel?.toLowerCase()}`}>
                          {riskLevel}
                        </span>
                      </td>
                      <td>{riskScore.toFixed(1)}</td>
                      <td>{new Date(analysis.timestamp).toLocaleString()}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
