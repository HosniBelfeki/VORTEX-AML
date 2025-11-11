import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  Search, 
  Upload, 
  FileText, 
  List, 
  Briefcase, 
  BarChart3,
  Menu,
  X,
  Shield
} from 'lucide-react'
import './Layout.css'

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()

  const menuItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/screening', icon: Search, label: 'Manual Screening' },
    { path: '/upload', icon: Upload, label: 'Document Upload' },
    { path: '/bulk', icon: FileText, label: 'Bulk Analysis' },
    { path: '/analyses', icon: List, label: 'All Analyses' },
    { path: '/cases', icon: Briefcase, label: 'Compliance Cases' },
    { path: '/reports', icon: BarChart3, label: 'Reports' },
  ]

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="logo">
            <Shield size={32} />
            {sidebarOpen && <span>VORTEX-AML</span>}
          </div>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${isActive ? 'active' : ''}`}
                title={item.label}
              >
                <Icon size={20} />
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            )
          })}
        </nav>

        <button 
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </aside>

      {/* Main Content */}
      <div className="main-wrapper">
        <header className="header">
          <div className="header-content">
            <h1 className="page-title">
              {menuItems.find(item => item.path === location.pathname)?.label || 'VORTEX-AML'}
            </h1>
            <div className="header-actions">
              <div className="status-badge">
                <span className="status-dot"></span>
                System Operational
              </div>
            </div>
          </div>
        </header>

        <main className="main-content">
          <div className="container">
            {children}
          </div>
        </main>

        <footer className="footer">
          <div className="container">
            <p>© 2025 VORTEX-AML | Enterprise Anti-Money Laundering Platform</p>
            <p>Developed by <a href="https://www.linkedin.com/in/hosnibelfeki/" target="_blank" rel="noopener noreferrer">Hosni Belfeki</a></p>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default Layout
