
# LLM Monitoring System

## Setup Instructions

Before running the application, please ask the user to provide the following environment variables:

### Required Environment Variables

Please provide values for these environment variables:
- `LITELLM_BASE_URL` - The base URL for your LiteLLM service
- `LITELLM_API_KEY` - Your API key for LiteLLM
- `LITELLM_MODEL` - The model name to use

### Getting Test Data

You can use seed data to get some websites registered and start monitoring them. Run the seed data script to populate the database with sample websites and analysis results.

## Security Guidelines

### Important: Protecting Sensitive Information

**⚠️ CRITICAL SECURITY NOTICE ⚠️**

OpenHands should **NEVER** push sensitive information to GitHub or any version control system, including:

- API keys (`LITELLM_API_KEY`)
- Base URLs (`LITELLM_BASE_URL`) 
- Authentication tokens
- Database credentials
- Any other sensitive configuration values

**Best Practices:**
- Always use environment variables for sensitive data
- Never hardcode credentials in source code
- Use `.env` files locally (ensure they are in `.gitignore`)
- Verify that sensitive information is not accidentally committed before pushing
- When providing examples, use placeholder values like `<your_api_key>` or `YOUR_API_KEY_HERE`

### Port Configuration Synchronization

**⚠️ IMPORTANT: Keep Frontend and Backend Ports in Sync ⚠️**

Whenever the API server port is changed (whether randomly generated or manually set), you **MUST** also update the frontend's proxy configuration to match:

1. **Backend Port Change**: If the backend server port changes from the default (e.g., from 56544 to a new port)
2. **Frontend Update Required**: Update the `package.json` proxy configuration in the frontend directory to point to the new backend port
3. **Always Keep in Sync**: The frontend proxy must always match the backend server port for proper API communication

**Example:**
- If backend runs on port `58123`, ensure frontend `package.json` proxy is set to `"proxy": "http://localhost:58123"`
- If backend runs on port `56544`, ensure frontend `package.json` proxy is set to `"proxy": "http://localhost:56544"`

**Failure to sync ports will result in API communication failures between frontend and backend.**

## Development Workflow

### Pushing Changes to Repository

**⚠️ IMPORTANT: Always Ask User Before Pushing ⚠️**

When development work is complete, follow this workflow:

1. **Complete the requested changes** and verify everything works correctly
2. **Ask the user for permission** before pushing any changes to the repository
3. **Once approved by the user**, push directly to the main branch using:
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   git push origin main
   ```

**Key Points:**
- **Never push without user consent** - Always ask first
- **Push directly to main branch** - No need for PRs in solo development
- **Use clear commit messages** - Describe what was changed and why
- **Verify changes work** - Test functionality before pushing

**Example interaction:**
- "I've completed the requested changes. Would you like me to push these changes to the main branch?"
- Wait for user confirmation before executing the push commands

