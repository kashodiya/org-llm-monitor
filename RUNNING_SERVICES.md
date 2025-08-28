
# LLM Monitoring System - Running Services

## 🚀 Services Status

Both the backend and frontend services are now running successfully!

### Backend API Server
- **Status**: ✅ Running
- **Port**: 51183
- **URL**: http://localhost:51183
- **Health Check**: http://localhost:51183/api/health
- **API Documentation**: http://localhost:51183/docs (FastAPI auto-generated docs)

### Frontend React Application
- **Status**: ✅ Running  
- **Port**: 55447
- **URL**: http://localhost:55447
- **Development Server**: React development server with hot reload

## 📊 Database Status

- **Database**: SQLite (`monitoring.db`)
- **Websites**: 12 Federal Reserve Bank districts loaded
- **Questions**: 60 monitoring questions (5 per website)
- **Status**: ✅ Seeded and ready

## 🔗 Available API Endpoints

### Websites
- `GET /api/websites` - List all websites
- `POST /api/websites` - Add new website
- `DELETE /api/websites/{id}` - Deactivate website

### Monitoring
- `POST /api/monitoring/start` - Start monitoring
- `GET /api/monitoring/status` - Get monitoring status
- `POST /api/monitoring/schedule` - Setup scheduled monitoring

### Analysis
- `GET /api/analysis/results` - Get analysis results
- `GET /api/analysis/summary` - Get misrepresentations summary

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## 🏦 Seeded Federal Reserve Banks

1. **1st District (Boston)** - https://www.bostonfed.org/
2. **2nd District (New York)** - https://www.newyorkfed.org/
3. **3rd District (Philadelphia)** - https://www.philadelphiafed.org/
4. **4th District (Cleveland)** - https://www.clevelandfed.org/
5. **5th District (Richmond)** - https://www.richmondfed.org/
6. **6th District (Atlanta)** - https://www.atlantafed.org/
7. **7th District (Chicago)** - https://www.chicagofed.org/
8. **8th District (St. Louis)** - https://www.stlouisfed.org/
9. **9th District (Minneapolis)** - https://www.minneapolisfed.org/
10. **10th District (Kansas City)** - https://www.kansascityfed.org/
11. **11th District (Dallas)** - https://www.dallasfed.org/
12. **12th District (San Francisco)** - https://www.frbsf.org/

## 🛠️ Management Commands

### Stop Services
```bash
# Stop backend
kill %1

# Stop frontend  
kill %2
```

### Restart Services

#### Linux/macOS
```bash
# Restart backend
cd /workspace/org-llm-monitor
PORT=51183 python3 main.py > backend.log 2>&1 &

# Restart frontend
cd /workspace/org-llm-monitor/frontend
npm start > frontend.log 2>&1 &
```

#### Windows
```cmd
# Restart backend
cd /workspace/org-llm-monitor
set PORT=51183 && python main.py

# Restart frontend
cd /workspace/org-llm-monitor/frontend
npm run startw
```

### View Logs
```bash
# Backend logs
tail -f /workspace/org-llm-monitor/backend.log

# Frontend logs
tail -f /workspace/org-llm-monitor/frontend/frontend.log
```

## 🔧 Configuration

### Backend Configuration
- Host: 0.0.0.0 (accessible from any interface)
- Port: 51183
- Debug: Enabled
- CORS: Enabled for all origins

### Frontend Configuration
- Host: 0.0.0.0 (accessible from any interface)
- Port: 55447 (Linux/macOS) / 55914 (Windows)
- Proxy: http://localhost:51183 (backend API)
- Hot Reload: Enabled
- Scripts:
  - `npm start` - Linux/macOS compatible start command
  - `npm run startw` - Windows compatible start command

## 🎯 Next Steps

1. **Access the Frontend**: 
   - Linux/macOS: Open http://localhost:55447 in your browser
   - Windows: Open http://localhost:55914 in your browser
2. **Explore the API**: Visit http://localhost:51183/docs for interactive API documentation
3. **Start Monitoring**: Use the frontend or API to begin monitoring the Federal Reserve websites
4. **View Results**: Check the dashboard for analysis results and misrepresentation detection

## 🖥️ Platform-Specific Instructions

### Windows Users
- Use `npm run startw` to start the frontend (runs on port 55914)
- Use `set PORT=51183 && python main.py` to start the backend
- Access frontend at http://localhost:55914

### Linux/macOS Users  
- Use `npm start` to start the frontend (runs on port 55447)
- Use `PORT=51183 python3 main.py` to start the backend
- Access frontend at http://localhost:55447

The system is now ready to monitor how LLM services represent the Federal Reserve Bank websites!

