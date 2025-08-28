











import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const Monitoring = () => {
  const navigate = useNavigate();
  const [websites, setWebsites] = useState([]);
  const [monitoringStatus, setMonitoringStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedWebsites, setSelectedWebsites] = useState([]);
  const [sessionName, setSessionName] = useState('');
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [scheduledInterval, setScheduledInterval] = useState(6);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [websitesResponse, statusResponse] = await Promise.all([
        apiService.getWebsites(true), // Only active websites
        apiService.getMonitoringStatus()
      ]);
      
      setWebsites(websitesResponse.data);
      setMonitoringStatus(statusResponse.data);
    } catch (err) {
      console.error('Error loading monitoring data:', err);
      setError('Failed to load monitoring data. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleWebsiteSelection = (websiteId) => {
    setSelectedWebsites(prev => {
      if (prev.includes(websiteId)) {
        return prev.filter(id => id !== websiteId);
      } else {
        return [...prev, websiteId];
      }
    });
  };

  const selectAllWebsites = () => {
    if (selectedWebsites.length === websites.length) {
      setSelectedWebsites([]);
    } else {
      setSelectedWebsites(websites.map(w => w.id));
    }
  };

  const startMonitoring = async () => {
    try {
      setIsMonitoring(true);
      setError(null);
      
      const requestData = {
        website_ids: selectedWebsites.length > 0 ? selectedWebsites : undefined,
        session_name: sessionName || undefined
      };
      
      await apiService.startMonitoring(requestData);
      
      // Refresh status
      await loadData();
      
      // Navigate to Results tab instead of showing alert
      navigate('/results');
      
    } catch (err) {
      console.error('Error starting monitoring:', err);
      setError(err.response?.data?.detail || 'Failed to start monitoring.');
    } finally {
      setIsMonitoring(false);
    }
  };

  const setupScheduledMonitoring = async () => {
    try {
      setError(null);
      await apiService.setupScheduledMonitoring(scheduledInterval);
      await loadData();
      alert(`Scheduled monitoring set up successfully! Will run every ${scheduledInterval} hours.`);
    } catch (err) {
      console.error('Error setting up scheduled monitoring:', err);
      setError('Failed to set up scheduled monitoring.');
    }
  };

  const stopScheduledMonitoring = async () => {
    try {
      setError(null);
      await apiService.stopScheduledMonitoring();
      await loadData();
      alert('Scheduled monitoring stopped successfully.');
    } catch (err) {
      console.error('Error stopping scheduled monitoring:', err);
      setError('Failed to stop scheduled monitoring.');
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading Monitoring Configuration...</h2>
      </div>
    );
  }

  return (
    <div>
      <h1>Monitoring Control</h1>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {/* Current Status */}
      <div className="card">
        <h2>Current Status</h2>
        {monitoringStatus && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
              <div>
                <strong>System Status:</strong>
                <span className={`status-badge ${monitoringStatus.is_running ? 'status-active' : 'status-inactive'}`}>
                  {monitoringStatus.is_running ? 'Running' : 'Stopped'}
                </span>
              </div>
              <div>
                <strong>Active Websites:</strong> {monitoringStatus.active_websites}
              </div>
              <div>
                <strong>Scheduled Jobs:</strong> {monitoringStatus.scheduled_jobs}
              </div>
              {monitoringStatus.current_session_id && (
                <div>
                  <strong>Current Session:</strong> #{monitoringStatus.current_session_id}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Manual Monitoring */}
      <div className="card">
        <h2>Start Manual Monitoring</h2>
        
        {websites.length === 0 ? (
          <div className="alert alert-warning">
            <p>No active websites found. Please add and activate websites in the Websites section before starting monitoring.</p>
          </div>
        ) : (
          <div>
            <div className="form-group">
              <label className="form-label">Session Name (Optional)</label>
              <input
                type="text"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                className="form-input"
                placeholder="e.g., Weekly Review - March 2024"
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Select Websites to Monitor
                <button 
                  type="button"
                  onClick={selectAllWebsites}
                  style={{ marginLeft: '10px', fontSize: '12px' }}
                  className="btn btn-secondary"
                >
                  {selectedWebsites.length === websites.length ? 'Deselect All' : 'Select All'}
                </button>
              </label>
              
              <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #ddd', padding: '10px', borderRadius: '4px' }}>
                {websites.map((website) => (
                  <div key={website.id} style={{ marginBottom: '8px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={selectedWebsites.includes(website.id)}
                        onChange={() => handleWebsiteSelection(website.id)}
                        style={{ marginRight: '8px' }}
                      />
                      <div>
                        <strong>{website.name}</strong>
                        <br />
                        <small style={{ color: '#666' }}>{website.url}</small>
                      </div>
                    </label>
                  </div>
                ))}
              </div>
              
              <small style={{ color: '#666', marginTop: '5px', display: 'block' }}>
                Leave empty to monitor all active websites
              </small>
            </div>

            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <button
                className="btn btn-primary"
                onClick={startMonitoring}
                disabled={isMonitoring}
              >
                {isMonitoring ? 'Starting Monitoring...' : 'Start Monitoring Now'}
              </button>
              
              {selectedWebsites.length > 0 && (
                <span style={{ color: '#666' }}>
                  ({selectedWebsites.length} website{selectedWebsites.length !== 1 ? 's' : ''} selected)
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Scheduled Monitoring */}
      <div className="card">
        <h2>Scheduled Monitoring</h2>
        
        <p>Set up automatic monitoring to run at regular intervals.</p>
        
        <div className="form-group">
          <label className="form-label">Monitoring Interval (Hours)</label>
          <select
            value={scheduledInterval}
            onChange={(e) => setScheduledInterval(parseInt(e.target.value))}
            className="form-input"
            style={{ width: 'auto' }}
          >
            <option value={1}>Every Hour</option>
            <option value={3}>Every 3 Hours</option>
            <option value={6}>Every 6 Hours</option>
            <option value={12}>Every 12 Hours</option>
            <option value={24}>Daily</option>
            <option value={168}>Weekly</option>
          </select>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            className="btn btn-success"
            onClick={setupScheduledMonitoring}
            disabled={websites.length === 0}
          >
            Start Scheduled Monitoring
          </button>
          
          {monitoringStatus?.scheduled_jobs > 0 && (
            <button
              className="btn btn-danger"
              onClick={stopScheduledMonitoring}
            >
              Stop Scheduled Monitoring
            </button>
          )}
        </div>
      </div>

      {/* Monitoring Process Information */}
      <div className="card">
        <h2>How Monitoring Works</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div>
            <h3>1. Content Scraping</h3>
            <p>The system visits each selected website and extracts the main content, including text, headings, and key information.</p>
          </div>
          
          <div>
            <h3>2. Question Generation</h3>
            <p>Based on the scraped content, the system generates relevant questions that test knowledge about your organization.</p>
          </div>
          
          <div>
            <h3>3. LLM Querying</h3>
            <p>These questions are sent to external LLM services to see how they respond about your organization.</p>
          </div>
          
          <div>
            <h3>4. Accuracy Analysis</h3>
            <p>The LLM responses are compared against your actual website content to detect misrepresentations.</p>
          </div>
        </div>

        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <h3>Monitoring Tips</h3>
          <ul>
            <li><strong>Regular Monitoring:</strong> Set up scheduled monitoring to catch changes over time</li>
            <li><strong>Content Updates:</strong> Run manual monitoring after updating important content</li>
            <li><strong>Comprehensive Coverage:</strong> Include all key pages that represent your organization</li>
            <li><strong>Review Results:</strong> Regularly check the Results page for detected misrepresentations</li>
          </ul>
        </div>
      </div>

      {/* Recent Activity */}
      {monitoringStatus?.current_session_id && (
        <div className="card">
          <h2>Current Activity</h2>
          <div className="alert alert-warning">
            <p><strong>Monitoring in Progress</strong></p>
            <p>Session #{monitoringStatus.current_session_id} is currently running. Check the Results page for real-time updates.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Monitoring;











