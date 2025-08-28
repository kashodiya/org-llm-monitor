














import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const Results = () => {
  const [analysisResults, setAnalysisResults] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);
  const [filterMisrepresentations, setFilterMisrepresentations] = useState(false);
  const [sortBy, setSortBy] = useState('date');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadResults();
  }, []);

  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(() => {
        refreshResults();
      }, 5000); // Refresh every 5 seconds
    }
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [autoRefresh]);

  const loadResults = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [resultsResponse, summaryResponse] = await Promise.all([
        apiService.getAnalysisResults(100),
        apiService.getMisrepresentationsSummary()
      ]);
      
      setAnalysisResults(resultsResponse.data);
      setSummary(summaryResponse.data);
    } catch (err) {
      console.error('Error loading results:', err);
      setError('Failed to load analysis results. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const refreshResults = async () => {
    try {
      setRefreshing(true);
      setError(null);
      
      const [resultsResponse, summaryResponse] = await Promise.all([
        apiService.getAnalysisResults(100),
        apiService.getMisrepresentationsSummary()
      ]);
      
      setAnalysisResults(resultsResponse.data);
      setSummary(summaryResponse.data);
    } catch (err) {
      console.error('Error refreshing results:', err);
      setError('Failed to refresh analysis results. Please check if the API server is running.');
    } finally {
      setRefreshing(false);
    }
  };

  const getFilteredAndSortedResults = () => {
    let filtered = analysisResults;
    
    if (filterMisrepresentations) {
      filtered = filtered.filter(result => result.misrepresentation_detected);
    }
    
    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.analyzed_at) - new Date(a.analyzed_at);
        case 'accuracy':
          return a.accuracy_score - b.accuracy_score;
        case 'website':
          return a.website_name.localeCompare(b.website_name);
        default:
          return 0;
      }
    });
  };

  const getAccuracyColor = (score) => {
    if (score >= 0.8) return '#28a745'; // Green
    if (score >= 0.6) return '#ffc107'; // Yellow
    return '#dc3545'; // Red
  };

  const getAccuracyLabel = (score) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const openResultDetails = (result) => {
    setSelectedResult(result);
  };

  const closeResultDetails = () => {
    setSelectedResult(null);
  };

  if (loading) {
    return (
      <div className="loading">
        <h2>Loading Analysis Results...</h2>
      </div>
    );
  }

  const filteredResults = getFilteredAndSortedResults();

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Analysis Results</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              style={{ marginRight: '8px' }}
            />
            Auto Refresh (5s) {autoRefresh && refreshing && '🔄'}
          </label>
          <button 
            className="btn btn-primary" 
            onClick={refreshResults}
            disabled={refreshing}
          >
            {refreshing ? '🔄 Refreshing...' : 'Refresh Results'}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {/* Summary Statistics */}
      {summary && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{summary.total_misrepresentations}</div>
            <div className="stat-label">Total Misrepresentations</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{summary.by_website?.length || 0}</div>
            <div className="stat-label">Affected Websites</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{summary.recent_misrepresentations?.length || 0}</div>
            <div className="stat-label">Recent Issues</div>
          </div>
        </div>
      )}

      {/* Filters and Sorting */}
      <div className="card">
        <h2>Filter & Sort Results</h2>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', alignItems: 'center' }}>
            <input
              type="checkbox"
              checked={filterMisrepresentations}
              onChange={(e) => setFilterMisrepresentations(e.target.checked)}
              style={{ marginRight: '8px' }}
            />
            Show only misrepresentations
          </label>
          
          <div>
            <label style={{ marginRight: '8px' }}>Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="form-input"
              style={{ width: 'auto' }}
            >
              <option value="date">Date (Newest First)</option>
              <option value="accuracy">Accuracy (Lowest First)</option>
              <option value="website">Website Name</option>
            </select>
          </div>
          
          <div style={{ color: '#666' }}>
            Showing {filteredResults.length} of {analysisResults.length} results
          </div>
        </div>
      </div>

      {/* Results List */}
      <div className="card">
        <h2>Analysis Results</h2>
        
        {filteredResults.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            {analysisResults.length === 0 ? (
              <div>
                <p>No analysis results found.</p>
                <p>Start monitoring your websites to see results here.</p>
              </div>
            ) : (
              <p>No results match the current filters.</p>
            )}
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Website</th>
                  <th>Question</th>
                  <th>Accuracy</th>
                  <th>Status</th>
                  <th>Analyzed</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.map((result) => (
                  <tr key={result.id}>
                    <td>
                      <strong>{result.website_name}</strong>
                      <br />
                      <small style={{ color: '#666' }}>{result.website_url}</small>
                    </td>
                    <td>
                      <div style={{ maxWidth: '300px' }}>
                        {result.question_text.length > 100 
                          ? `${result.question_text.substring(0, 100)}...`
                          : result.question_text
                        }
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div
                          style={{
                            width: '60px',
                            height: '20px',
                            backgroundColor: '#f0f0f0',
                            borderRadius: '10px',
                            overflow: 'hidden'
                          }}
                        >
                          <div
                            style={{
                              width: `${result.accuracy_score * 100}%`,
                              height: '100%',
                              backgroundColor: getAccuracyColor(result.accuracy_score),
                              transition: 'width 0.3s ease'
                            }}
                          />
                        </div>
                        <span style={{ fontSize: '0.9em', color: getAccuracyColor(result.accuracy_score) }}>
                          {(result.accuracy_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td>
                      {result.misrepresentation_detected ? (
                        <span className="status-badge status-inactive">⚠️ Misrepresentation</span>
                      ) : (
                        <span className="status-badge status-active">✅ Accurate</span>
                      )}
                    </td>
                    <td>
                      {formatDate(result.analyzed_at)}
                    </td>
                    <td>
                      <button
                        className="btn btn-primary"
                        style={{ fontSize: '12px', padding: '5px 10px' }}
                        onClick={() => openResultDetails(result)}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Misrepresentations by Website */}
      {summary?.by_website && summary.by_website.length > 0 && (
        <div className="card">
          <h2>Misrepresentations by Website</h2>
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Website</th>
                  <th>URL</th>
                  <th>Misrepresentations</th>
                </tr>
              </thead>
              <tbody>
                {summary.by_website.map((website, index) => (
                  <tr key={index}>
                    <td><strong>{website.name}</strong></td>
                    <td>
                      <a href={website.url} target="_blank" rel="noopener noreferrer">
                        {website.url}
                      </a>
                    </td>
                    <td>
                      <span className="status-badge status-inactive">
                        {website.misrepresentation_count}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Result Details Modal */}
      {selectedResult && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '30px',
            maxWidth: '800px',
            maxHeight: '80vh',
            overflow: 'auto',
            width: '100%'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2>Analysis Details</h2>
              <button
                onClick={closeResultDetails}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '24px',
                  cursor: 'pointer',
                  color: '#666'
                }}
              >
                ×
              </button>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h3>Website Information</h3>
              <p><strong>Name:</strong> {selectedResult.website_name}</p>
              <p><strong>URL:</strong> <a href={selectedResult.website_url} target="_blank" rel="noopener noreferrer">{selectedResult.website_url}</a></p>
              <p><strong>Content Title:</strong> {selectedResult.content_title}</p>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h3>Question Asked</h3>
              <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
                {selectedResult.question_text}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h3>LLM Response</h3>
              <p><strong>Service:</strong> {selectedResult.llm_service}</p>
              <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px', maxHeight: '200px', overflow: 'auto' }}>
                {selectedResult.response_text}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h3>Analysis Results</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                <div>
                  <strong>Accuracy Score:</strong>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '5px' }}>
                    <div
                      style={{
                        width: '100px',
                        height: '20px',
                        backgroundColor: '#f0f0f0',
                        borderRadius: '10px',
                        overflow: 'hidden'
                      }}
                    >
                      <div
                        style={{
                          width: `${selectedResult.accuracy_score * 100}%`,
                          height: '100%',
                          backgroundColor: getAccuracyColor(selectedResult.accuracy_score)
                        }}
                      />
                    </div>
                    <span style={{ color: getAccuracyColor(selectedResult.accuracy_score) }}>
                      {(selectedResult.accuracy_score * 100).toFixed(1)}% ({getAccuracyLabel(selectedResult.accuracy_score)})
                    </span>
                  </div>
                </div>
                
                <div>
                  <strong>Misrepresentation:</strong>
                  <div style={{ marginTop: '5px' }}>
                    {selectedResult.misrepresentation_detected ? (
                      <span className="status-badge status-inactive">⚠️ Detected</span>
                    ) : (
                      <span className="status-badge status-active">✅ None</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {selectedResult.analysis_details && (
              <div style={{ marginBottom: '20px' }}>
                <h3>Detailed Analysis</h3>
                <div style={{ 
                  padding: '15px', 
                  backgroundColor: '#f8f9fa', 
                  borderRadius: '4px',
                  maxHeight: '200px',
                  overflow: 'auto',
                  fontSize: '0.9em'
                }}>
                  <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                    {selectedResult.analysis_details}
                  </pre>
                </div>
              </div>
            )}

            <div style={{ textAlign: 'right' }}>
              <button className="btn btn-primary" onClick={closeResultDetails}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Results;














