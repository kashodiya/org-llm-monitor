














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
        <div 
          style={{
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
          }}
          onClick={closeResultDetails} // Click outside to close
        >
          <div 
            style={{
              backgroundColor: 'white',
              borderRadius: '8px',
              padding: '30px',
              maxWidth: '800px',
              maxHeight: '80vh',
              overflow: 'auto',
              width: '100%',
              position: 'relative'
            }}
            onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside modal
          >
            {/* Fixed close button */}
            <button
              onClick={closeResultDetails}
              style={{
                position: 'sticky',
                top: '10px',
                right: '10px',
                float: 'right',
                background: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '50%',
                width: '35px',
                height: '35px',
                fontSize: '18px',
                cursor: 'pointer',
                color: '#666',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 10,
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                marginBottom: '10px'
              }}
              onMouseOver={(e) => {
                e.target.style.backgroundColor = '#e9ecef';
                e.target.style.color = '#000';
              }}
              onMouseOut={(e) => {
                e.target.style.backgroundColor = '#f8f9fa';
                e.target.style.color = '#666';
              }}
            >
              ×
            </button>
            
            <div style={{ clear: 'both', marginBottom: '20px' }}>
              <h2>Analysis Details</h2>
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
                {(() => {
                  try {
                    const analysisData = JSON.parse(selectedResult.analysis_details);
                    return (
                      <div style={{ 
                        padding: '20px', 
                        backgroundColor: '#f8f9fa', 
                        borderRadius: '8px',
                        border: '1px solid #e9ecef'
                      }}>
                        {/* Analysis Summary */}
                        {analysisData.analysis_summary && (
                          <div style={{ marginBottom: '20px' }}>
                            <h4 style={{ color: '#495057', marginBottom: '10px', fontSize: '1.1em' }}>
                              📋 Analysis Summary
                            </h4>
                            <div style={{ 
                              padding: '12px', 
                              backgroundColor: 'white', 
                              borderRadius: '4px',
                              border: '1px solid #dee2e6',
                              lineHeight: '1.5'
                            }}>
                              {analysisData.analysis_summary}
                            </div>
                          </div>
                        )}

                        {/* Confidence Score */}
                        {analysisData.confidence !== undefined && (
                          <div style={{ marginBottom: '20px' }}>
                            <h4 style={{ color: '#495057', marginBottom: '10px', fontSize: '1.1em' }}>
                              🎯 Analysis Confidence
                            </h4>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                              <div style={{
                                width: '120px',
                                height: '20px',
                                backgroundColor: '#e9ecef',
                                borderRadius: '10px',
                                overflow: 'hidden'
                              }}>
                                <div style={{
                                  width: `${analysisData.confidence * 100}%`,
                                  height: '100%',
                                  backgroundColor: analysisData.confidence >= 0.8 ? '#28a745' : 
                                                 analysisData.confidence >= 0.6 ? '#ffc107' : '#dc3545',
                                  transition: 'width 0.3s ease'
                                }} />
                              </div>
                              <span style={{ 
                                fontWeight: 'bold',
                                color: analysisData.confidence >= 0.8 ? '#28a745' : 
                                       analysisData.confidence >= 0.6 ? '#ffc107' : '#dc3545'
                              }}>
                                {(analysisData.confidence * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        )}

                        {/* Specific Issues */}
                        {analysisData.specific_issues && analysisData.specific_issues.length > 0 && (
                          <div style={{ marginBottom: '20px' }}>
                            <h4 style={{ color: '#495057', marginBottom: '10px', fontSize: '1.1em' }}>
                              ⚠️ Specific Issues Found
                            </h4>
                            <div style={{ 
                              padding: '12px', 
                              backgroundColor: 'white', 
                              borderRadius: '4px',
                              border: '1px solid #dee2e6'
                            }}>
                              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                {analysisData.specific_issues.map((issue, index) => (
                                  <li key={index} style={{ 
                                    marginBottom: '8px', 
                                    lineHeight: '1.4',
                                    color: '#dc3545'
                                  }}>
                                    {issue}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        )}

                        {/* Raw Analysis (Collapsible) */}
                        {analysisData.raw_analysis && (
                          <div style={{ marginBottom: '10px' }}>
                            <details style={{ cursor: 'pointer' }}>
                              <summary style={{ 
                                color: '#495057', 
                                fontSize: '1.1em',
                                fontWeight: 'bold',
                                marginBottom: '10px',
                                padding: '8px',
                                backgroundColor: 'white',
                                borderRadius: '4px',
                                border: '1px solid #dee2e6'
                              }}>
                                🔍 Full Analysis Details
                              </summary>
                              <div style={{ 
                                padding: '15px', 
                                backgroundColor: 'white', 
                                borderRadius: '4px',
                                border: '1px solid #dee2e6',
                                marginTop: '10px',
                                maxHeight: '300px',
                                overflow: 'auto'
                              }}>
                                <pre style={{ 
                                  whiteSpace: 'pre-wrap', 
                                  margin: 0,
                                  fontSize: '0.9em',
                                  lineHeight: '1.4',
                                  color: '#495057'
                                }}>
                                  {analysisData.raw_analysis}
                                </pre>
                              </div>
                            </details>
                          </div>
                        )}
                      </div>
                    );
                  } catch (error) {
                    // Fallback for malformed JSON
                    return (
                      <div style={{ 
                        padding: '15px', 
                        backgroundColor: '#f8f9fa', 
                        borderRadius: '4px',
                        border: '1px solid #e9ecef'
                      }}>
                        <div style={{ 
                          padding: '10px', 
                          backgroundColor: '#fff3cd', 
                          borderRadius: '4px',
                          border: '1px solid #ffeaa7',
                          marginBottom: '15px',
                          color: '#856404'
                        }}>
                          ⚠️ Unable to parse analysis details. Showing raw data:
                        </div>
                        <pre style={{ 
                          whiteSpace: 'pre-wrap', 
                          margin: 0,
                          fontSize: '0.9em',
                          maxHeight: '200px',
                          overflow: 'auto',
                          padding: '10px',
                          backgroundColor: 'white',
                          borderRadius: '4px',
                          border: '1px solid #dee2e6'
                        }}>
                          {selectedResult.analysis_details}
                        </pre>
                      </div>
                    );
                  }
                })()}
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














