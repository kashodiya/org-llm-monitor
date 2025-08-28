
# LLM Monitoring System

## Setup Instructions

Before running the application, please ask the user to provide the following environment variables:

### Required Environment Variables

Please provide values for these environment variables:
- `LITELLM_BASE_URL` - The base URL for your LiteLLM service
- `LITELLM_API_KEY` - Your API key for LiteLLM
- `LITELLM_MODEL` - The model name to use

### Running the Application

1. **Backend**: Start the backend server on port 56544
   ```bash
   cd /workspace/org-llm-monitor
   LITELLM_BASE_URL=<your_base_url> LITELLM_API_KEY=<your_api_key> LITELLM_MODEL=<your_model> PORT=56544 python main.py
   ```

2. **Frontend**: Start the frontend server on port 53134
   ```bash
   cd /workspace/org-llm-monitor/frontend
   npm install
   npm start
   ```

3. **Access the Application**: 
   - Frontend: http://localhost:53134
   - Backend API: http://localhost:56544

### Getting Test Data

You can use seed data to get some websites registered and start monitoring them. Run the seed data script to populate the database with sample websites and analysis results.

### Auto-Refresh Feature

The Results page now includes an improved auto-refresh functionality that:
- Updates data every 5 seconds when enabled
- Does not cause page flicker or reload the entire page
- Shows subtle visual indicators during refresh operations
- Maintains user interface state during updates

