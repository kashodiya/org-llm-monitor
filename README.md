# LLM Monitoring System

A comprehensive monitoring system for governmental organizations to track how Large Language Model (LLM) services represent their content and detect potential misrepresentations.

## Overview

This system continuously monitors how LLM services like ChatGPT represent your organization by:
- Scraping content from your public websites
- Generating relevant questions about your content
- Querying LLM services with these questions
- Analyzing responses for accuracy and detecting misrepresentations
- Providing a web dashboard to view results and trends

## Features

- **Website Monitoring**: Automatically scrape and monitor multiple websites
- **LLM Integration**: Query various LLM services through LiteLLM proxy
- **Misrepresentation Detection**: AI-powered analysis to detect inaccuracies
- **Web Dashboard**: React-based frontend for monitoring and analysis
- **REST API**: Full API for programmatic access
- **Database Storage**: SQLite database for storing results and history
- **Real-time Updates**: Live monitoring with configurable intervals

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI       │    │   SQLite        │
│   (Port 50014)  │◄──►│   Backend       │◄──►│   Database      │
│                 │    │   (Port 51183)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   LLM Services  │
                    │   (via LiteLLM) │
                    └─────────────────┘
```

## Technology Stack

### Backend
- **Python 3.12+** with uv package manager
- **FastAPI** for REST API
- **SQLite** for data storage
- **BeautifulSoup4** for web scraping
- **OpenAI SDK** for LLM integration
- **Uvicorn** for ASGI server

### Frontend
- **React 18** with functional components
- **React Router** for navigation
- **Axios** for API communication
- **Recharts** for data visualization
- **Material-UI** for UI components

## Installation

### Prerequisites
- Python 3.12+
- Node.js 16+
- uv package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd llm-monitoring-system
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment with uv
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   nano .env
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Database Initialization**
   ```bash
   # The database will be automatically created on first run
   python main.py
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# LLM Configuration
LITELLM_BASE_URL=http://your-litellm-proxy:7177
LITELLM_API_KEY=your-api-key
LITELLM_MODEL=your-model-name

# Database Configuration
DATABASE_PATH=./monitoring.db

# Server Configuration
API_HOST=0.0.0.0
API_PORT=51183
FRONTEND_PORT=50014

# Monitoring Configuration
SCRAPING_INTERVAL=3600  # seconds
MONITORING_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

### LiteLLM Proxy Setup

This system uses LiteLLM proxy to access various LLM services. Configure your proxy with:
- Base URL of your LiteLLM proxy server
- API key for authentication
- Model name to use for queries

## Usage

### Starting the System

1. **Start Backend Server**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:51183`

2. **Start Frontend Development Server**
   ```bash
   cd frontend
   npm start
   ```
   The web interface will be available at `http://localhost:50014`
   
   **Note**: The frontend is configured to bind to all network interfaces (0.0.0.0) to allow external access. This enables access from remote machines using the server's IP address.

### Web Interface

The system provides four main pages:

1. **Dashboard** (`/`)
   - Overview statistics
   - Recent activity
   - Misrepresentation trends
   - Quick access to key metrics

2. **Websites** (`/websites`)
   - Add/remove websites to monitor
   - View website status and last scrape time
   - Manual scraping triggers

3. **Monitoring** (`/monitoring`)
   - Start/stop monitoring processes
   - Configure monitoring intervals
   - View monitoring status and logs

4. **Results** (`/results`)
   - View all analysis results
   - Filter by misrepresentations
   - Detailed analysis reports
   - Export capabilities

### API Endpoints

#### Websites Management
- `GET /api/websites` - List all monitored websites
- `POST /api/websites` - Add new website
- `DELETE /api/websites/{id}` - Remove website

#### Monitoring Control
- `POST /api/monitoring/start` - Start monitoring
- `POST /api/monitoring/stop` - Stop monitoring
- `GET /api/monitoring/status` - Get monitoring status

#### Results and Analysis
- `GET /api/results` - Get analysis results
- `GET /api/results/{id}` - Get specific result details
- `GET /api/dashboard/stats` - Get dashboard statistics

#### System Health
- `GET /api/health` - System health check

### Adding Websites

1. Navigate to the Websites page
2. Click "Add Website"
3. Enter website details:
   - Name (display name)
   - URL (full URL to monitor)
   - Description (optional)
4. Click "Add Website"

The system will automatically:
- Scrape the website content
- Generate relevant questions
- Start monitoring the website

### Monitoring Process

The monitoring system works in cycles:

1. **Content Scraping**: Extract text content and key information from websites
2. **Question Generation**: Create relevant questions about the content
3. **LLM Querying**: Ask questions to configured LLM services
4. **Response Analysis**: Analyze LLM responses for accuracy
5. **Misrepresentation Detection**: Identify potential misrepresentations
6. **Storage**: Save results to database for reporting

### Understanding Results

#### Accuracy Scores
- **90-100%**: Highly accurate response
- **70-89%**: Generally accurate with minor issues
- **50-69%**: Partially accurate with notable problems
- **Below 50%**: Significant inaccuracies detected

#### Misrepresentation Detection
The system flags responses as misrepresentations when:
- Factual information contradicts website content
- Temporal information is incorrect (outdated/future)
- Key details are missing or misrepresented
- Context is significantly altered

## Development

### Project Structure

```
llm-monitoring-system/
├── src/
│   ├── api/                 # FastAPI application
│   ├── database/            # Database models and operations
│   ├── llm_client/          # LLM integration
│   ├── monitoring/          # Monitoring orchestration
│   └── web_scraper/         # Web scraping functionality
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── public/             # Static assets
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Running Tests

```bash
# Backend tests
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### Development Mode

For development, you can run both servers with auto-reload:

```bash
# Backend with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 51183

# Frontend with hot reload (binds to all interfaces)
cd frontend
npm start
```

## Deployment

### Production Build

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Configure Production Environment**
   ```bash
   # Update .env for production
   ENVIRONMENT=production
   DEBUG=false
   ```

3. **Run with Production Server**
   ```bash
   # Using gunicorn
   gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:51183
   ```

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 51183

CMD ["python", "main.py"]
```

## Security Considerations

- **API Keys**: Store LLM API keys securely in environment variables
- **Database**: Ensure SQLite database file has appropriate permissions
- **Network**: Use HTTPS in production environments
- **Rate Limiting**: Configure appropriate rate limits for LLM API calls
- **Input Validation**: All user inputs are validated and sanitized

## Troubleshooting

### Common Issues

1. **"Invalid Host header" Error**
   - Ensure `DANGEROUSLY_DISABLE_HOST_CHECK=true` is set in frontend start script
   - Check that HOST=0.0.0.0 is configured

2. **LLM API Connection Issues**
   - Verify LiteLLM proxy is running and accessible
   - Check API key and model configuration
   - Review network connectivity

3. **Database Errors**
   - Ensure SQLite database file is writable
   - Check disk space availability
   - Verify database schema is up to date

4. **Scraping Failures**
   - Check website accessibility
   - Verify SSL certificates
   - Review rate limiting settings

### Logs

System logs are available in:
- Backend: Console output with configurable log levels
- Frontend: Browser developer console
- Database: Query logs (if enabled)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Review the troubleshooting section
- Check the API documentation at `/docs` when the server is running

## Changelog

### Version 1.0.0
- Initial release
- Website monitoring functionality
- LLM integration via LiteLLM
- React-based dashboard
- Misrepresentation detection
- REST API with full CRUD operations
