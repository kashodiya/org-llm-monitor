








import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const Websites = () => {
  const [websites, setWebsites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    url: '',
    name: '',
    description: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadWebsites();
  }, []);

  const loadWebsites = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getWebsites(false); // Get all websites
      setWebsites(response.data);
    } catch (err) {
      console.error('Error loading websites:', err);
      setError('Failed to load websites. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.url || !formData.name) {
      setError('URL and Name are required fields.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      
      await apiService.createWebsite(formData);
      
      // Reset form and reload websites
      setFormData({ url: '', name: '', description: '' });
      setShowAddForm(false);
      await loadWebsites();
      
    } catch (err) {
      console.error('Error creating website:', err);
      setError(err.response?.data?.detail || 'Failed to add website. Please check the URL and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (websiteId, websiteName) => {
    if (!window.confirm(`Are you sure you want to deactivate "${websiteName}"?`)) {
      return;
    }

    try {
      await apiService.deleteWebsite(websiteId);
      await loadWebsites();
    } catch (err) {
      console.error('Error deleting website:', err);
      setError('Failed to deactivate website.');
    }
  };

  const getStatusBadge = (isActive) => {
    return isActive ? 
      <span className="status-badge status-active">Active</span> : 
      <span className="status-badge status-inactive">Inactive</span>;
  };

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading Websites...</h2>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Website Management</h1>
        <button 
          className="btn btn-primary"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Cancel' : 'Add Website'}
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {/* Add Website Form */}
      {showAddForm && (
        <div className="card">
          <h2>Add New Website</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Website URL *</label>
              <input
                type="url"
                name="url"
                value={formData.url}
                onChange={handleInputChange}
                className="form-input"
                placeholder="https://example.gov"
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Website Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Department of Example"
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                className="form-input"
                rows="3"
                placeholder="Brief description of the website and its purpose"
              />
            </div>
            
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                type="submit" 
                className="btn btn-success"
                disabled={submitting}
              >
                {submitting ? 'Adding...' : 'Add Website'}
              </button>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={() => setShowAddForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Websites List */}
      <div className="card">
        <h2>Monitored Websites ({websites.length})</h2>
        
        {websites.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            <p>No websites configured yet.</p>
            <p>Add your first website to start monitoring how LLMs represent your organization.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>URL</th>
                  <th>Description</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Last Scraped</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {websites.map((website) => (
                  <tr key={website.id}>
                    <td>
                      <strong>{website.name}</strong>
                    </td>
                    <td>
                      <a 
                        href={website.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ color: '#007bff', textDecoration: 'none' }}
                      >
                        {website.url}
                      </a>
                    </td>
                    <td>
                      {website.description || <em>No description</em>}
                    </td>
                    <td>
                      {getStatusBadge(website.is_active)}
                    </td>
                    <td>
                      {new Date(website.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      {website.last_scraped ? 
                        new Date(website.last_scraped).toLocaleDateString() : 
                        <em>Never</em>
                      }
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '5px' }}>
                        {website.is_active && (
                          <button
                            className="btn btn-danger"
                            style={{ fontSize: '12px', padding: '5px 10px' }}
                            onClick={() => handleDelete(website.id, website.name)}
                          >
                            Deactivate
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="card">
        <h2>Instructions</h2>
        <div>
          <h3>Adding Websites</h3>
          <ul>
            <li>Enter the full URL of your governmental website (must start with http:// or https://)</li>
            <li>Provide a descriptive name for easy identification</li>
            <li>Add an optional description explaining the website's purpose</li>
            <li>The system will validate the URL accessibility before adding it</li>
          </ul>
          
          <h3>Website Monitoring</h3>
          <ul>
            <li>Active websites are automatically included in monitoring sessions</li>
            <li>The system scrapes content and generates relevant questions</li>
            <li>Questions are sent to LLM services to test their knowledge</li>
            <li>Responses are analyzed for accuracy and potential misrepresentations</li>
          </ul>
          
          <h3>Best Practices</h3>
          <ul>
            <li>Monitor your main organizational pages (About, Services, Leadership)</li>
            <li>Include pages with frequently updated content (News, Announcements)</li>
            <li>Add pages containing important policy information</li>
            <li>Ensure websites are publicly accessible (not behind authentication)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Websites;








