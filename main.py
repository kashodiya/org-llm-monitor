
#!/usr/bin/env python3

"""
LLM Monitoring System - Main Entry Point

This is the main entry point for the LLM Monitoring System.
It starts the FastAPI server and initializes all components.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the application"""
    print("=" * 60)
    print("LLM MONITORING SYSTEM")
    print("=" * 60)
    print("Monitoring how LLM services represent governmental organizations")
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 51183))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"🌐 Server Configuration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print()
    
    print(f"🔗 Access URLs:")
    print(f"   API: http://localhost:{port}")
    print(f"   Health Check: http://localhost:{port}/api/health")
    print(f"   Dashboard: http://localhost:{port}/")
    print()
    
    print(f"🤖 LLM Configuration:")
    print(f"   Base URL: {os.getenv('LITELLM_BASE_URL', 'Not configured')}")
    print(f"   Model: {os.getenv('LITELLM_MODEL', 'Not configured')}")
    print()
    
    print("🚀 Starting server...")
    print("   Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Import and run the FastAPI app
        from src.api.main import app
        
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if debug else "warning",
            access_log=debug
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

