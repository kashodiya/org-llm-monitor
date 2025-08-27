






import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load dashboard stats and health status
      const [statsResponse, healthResponse] = await Promise.all([
        apiService.getDashboardStats(),
        apiService.healthCheck()
      ]);

      setStats(statsResponse.data);
      setHealthStatus(healthResponse.data);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const getHealthStatusBadge = (status) => {
    if (status === 'healthy') {
      return <span className="status-badge status-active">Healthy</span>;
    } else if (status === 'degraded') {
      return <span className="status-badge status-warning">Degraded</span>;
    } else {
      return <span className="status-badge status-inactive">Unhealthy</span>;
    }
  };

  const getComponentStatus = (component, status) => {
    return status ? 
      <span className="status-badge status-active">✓</span> : 
      <span className="status-badge status-inactive">✗</span>;
  };

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading Dashboard...</h2>
        <p>Please wait while we load the system status and statistics.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-error">
        <h3>Dashboard Error</h3>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={loadDashboardData}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1>LLM Monitoring Dashboard</h1>
      
      {/* System Health Status */}
      <div className="card">
        <h2>System Health</h2>
        {healthStatus && (
          <div>
            <p>
              <strong>Overall Status:</strong> {getHealthStatusBadge(healthStatus.status)}
              <span style={{ marginLeft: '10px', color: '#666' }}>
                Last checked: {new Date(healthStatus.timestamp).toLocaleString()}
              </span>
            </p>
            
            <h3>Component Status</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
              <div>
                <strong>Database:</strong> {getComponentStatus('database', healthStatus.components?.database)}
              </div>
              <div>
                <strong>LLM Client:</strong> {getComponentStatus('llm_client', healthStatus.components?.llm_client)}
              </div>
              <div>
                <strong>Web Scraper:</strong> {getComponentStatus('web_scraper', healthStatus.components?.web_scraper)}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Statistics */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{stats.total_websites}</div>
            <div className="stat-label">Active Websites</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{stats.total_analyses}</div>
            <div className="stat-label">Total Analyses</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{stats.total_misrepresentations}</div>
            <div className="stat-label">Misrepresentations Found</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{stats.recent_activity}</div>
            <div className="stat-label">Recent Activity (24h)</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{stats.average_accuracy}</div>
            <div className="stat-label">Average Accuracy</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{stats.misrepresentation_rate}%</div>
            <div className="stat-label">Misrepresentation Rate</div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h2>Quick Actions</h2>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button 
            className="btn btn-primary"
            onClick={() => window.location.href = '/monitoring'}
          >
            Start Monitoring
          </button>
          <button 
            className="btn btn-success"
            onClick={() => window.location.href = '/websites'}
          >
            Manage Websites
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => window.location.href = '/results'}
          >
            View Results
          </button>
          <button 
            className="btn btn-primary"
            onClick={loadDashboardData}
          >
            Refresh Data
          </button>
        </div>
      </div>

      {/* Recent Activity Summary */}
      {stats && stats.total_misrepresentations > 0 && (
        <div className="card">
          <h2>Alert Summary</h2>
          <div className="alert alert-warning">
            <strong>Attention:</strong> {stats.total_misrepresentations} misrepresentations have been detected 
            across your monitored websites. Please review the results page for detailed analysis.
          </div>
        </div>
      )}

      {/* System Information */}
      <div className="card">
        <h2>About This System</h2>
        <p>
          This LLM Monitoring System helps governmental organizations track how Large Language Models 
          represent their information. The system continuously monitors your websites and compares 
          LLM responses with actual content to detect misrepresentations.
        </p>
        
        <h3>Key Features:</h3>
        <ul>
          <li>Automated website content monitoring</li>
          <li>LLM query generation and testing</li>
          <li>Accuracy analysis and misrepresentation detection</li>
          <li>Scheduled monitoring with configurable intervals</li>
          <li>Comprehensive reporting and analytics</li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;






