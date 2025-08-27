




import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link';
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        <Link to="/" className="nav-brand">
          LLM Monitoring System
        </Link>
        <div className="nav-links">
          <Link to="/" className={isActive('/')}>
            Dashboard
          </Link>
          <Link to="/websites" className={isActive('/websites')}>
            Websites
          </Link>
          <Link to="/monitoring" className={isActive('/monitoring')}>
            Monitoring
          </Link>
          <Link to="/results" className={isActive('/results')}>
            Results
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;




