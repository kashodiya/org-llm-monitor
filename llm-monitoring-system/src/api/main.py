


from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
import sqlite3
from datetime import datetime

from ..database.models import DatabaseManager
from ..monitoring.monitor import MonitoringSystem

# Initialize FastAPI app
app = FastAPI(
    title="LLM Monitoring System",
    description="Monitor how LLM services represent governmental organizations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = DatabaseManager()
monitoring_system = MonitoringSystem()

print("API server initialized")

# Pydantic models
class WebsiteCreate(BaseModel):
    url: str
    name: str
    description: Optional[str] = ""

class WebsiteResponse(BaseModel):
    id: int
    url: str
    name: str
    description: Optional[str]
    is_active: bool
    created_at: str
    last_scraped: Optional[str]

class MonitoringRequest(BaseModel):
    website_ids: Optional[List[int]] = None
    session_name: Optional[str] = None

class QuestionCreate(BaseModel):
    website_id: int
    question_text: str
    category: Optional[str] = "manual"

# API Routes

@app.get("/")
async def root():
    """Root endpoint - serve the React frontend"""
    return {"message": "LLM Monitoring System API", "status": "running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    print("Health check requested")
    
    try:
        # Test system components
        test_results = monitoring_system.test_system_components()
        
        return {
            "status": "healthy" if test_results['overall'] else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": test_results
        }
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/api/websites", response_model=List[WebsiteResponse])
async def get_websites(active_only: bool = True):
    """Get all websites"""
    print(f"Getting websites (active_only: {active_only})")
    
    try:
        websites = db.get_websites(active_only=active_only)
        return websites
    except Exception as e:
        print(f"Error getting websites: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/websites", response_model=Dict)
async def create_website(website: WebsiteCreate):
    """Add a new website to monitor"""
    print(f"Creating website: {website.name} ({website.url})")
    
    try:
        website_id = monitoring_system.add_website_to_monitor(
            url=website.url,
            name=website.name,
            description=website.description
        )
        
        return {
            "id": website_id,
            "message": "Website added successfully",
            "success": True
        }
    except Exception as e:
        print(f"Error creating website: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/websites/{website_id}")
async def delete_website(website_id: int):
    """Deactivate a website"""
    print(f"Deactivating website ID: {website_id}")
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE websites SET is_active = 0 WHERE id = ?",
                (website_id,)
            )
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Website not found")
            
            conn.commit()
        
        return {"message": "Website deactivated successfully", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deactivating website: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/monitoring/start")
async def start_monitoring(request: MonitoringRequest, background_tasks: BackgroundTasks):
    """Start monitoring websites"""
    print(f"Starting monitoring with request: {request}")
    
    try:
        if request.website_ids:
            # Monitor specific websites
            def monitor_specific_websites():
                results = []
                for website_id in request.website_ids:
                    result = monitoring_system.monitor_website(website_id)
                    results.append(result)
                return results
            
            background_tasks.add_task(monitor_specific_websites)
            
            return {
                "message": f"Started monitoring {len(request.website_ids)} websites",
                "website_ids": request.website_ids,
                "success": True
            }
        else:
            # Monitor all websites
            background_tasks.add_task(monitoring_system.monitor_all_websites)
            
            return {
                "message": "Started monitoring all active websites",
                "success": True
            }
            
    except Exception as e:
        print(f"Error starting monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/status")
async def get_monitoring_status():
    """Get monitoring system status"""
    print("Getting monitoring status")
    
    try:
        status = monitoring_system.get_monitoring_status()
        return status
    except Exception as e:
        print(f"Error getting monitoring status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/monitoring/schedule")
async def setup_scheduled_monitoring(interval_hours: int = 6):
    """Setup scheduled monitoring"""
    print(f"Setting up scheduled monitoring every {interval_hours} hours")
    
    try:
        monitoring_system.setup_scheduled_monitoring(interval_hours)
        
        return {
            "message": f"Scheduled monitoring set up for every {interval_hours} hours",
            "interval_hours": interval_hours,
            "success": True
        }
    except Exception as e:
        print(f"Error setting up scheduled monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/monitoring/stop")
async def stop_scheduled_monitoring():
    """Stop scheduled monitoring"""
    print("Stopping scheduled monitoring")
    
    try:
        monitoring_system.stop_scheduled_monitoring()
        
        return {
            "message": "Scheduled monitoring stopped",
            "success": True
        }
    except Exception as e:
        print(f"Error stopping scheduled monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/results")
async def get_analysis_results(limit: int = 50):
    """Get recent analysis results"""
    print(f"Getting analysis results (limit: {limit})")
    
    try:
        results = db.get_recent_analysis_results(limit=limit)
        return results
    except Exception as e:
        print(f"Error getting analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/summary")
async def get_misrepresentations_summary():
    """Get summary of misrepresentations"""
    print("Getting misrepresentations summary")
    
    try:
        summary = db.get_misrepresentations_summary()
        return summary
    except Exception as e:
        print(f"Error getting misrepresentations summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/questions", response_model=Dict)
async def create_question(question: QuestionCreate):
    """Add a manual question"""
    print(f"Creating question for website ID: {question.website_id}")
    
    try:
        question_id = db.add_question(
            website_id=question.website_id,
            question_text=question.question_text,
            category=question.category
        )
        
        return {
            "id": question_id,
            "message": "Question added successfully",
            "success": True
        }
    except Exception as e:
        print(f"Error creating question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/questions/{website_id}")
async def get_questions_for_website(website_id: int):
    """Get questions for a specific website"""
    print(f"Getting questions for website ID: {website_id}")
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM questions 
                WHERE website_id = ? AND is_active = 1
                ORDER BY created_at DESC
            ''', (website_id,))
            
            questions = [dict(row) for row in cursor.fetchall()]
        
        return questions
    except Exception as e:
        print(f"Error getting questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    print("Getting dashboard statistics")
    
    try:
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Total websites
            cursor.execute("SELECT COUNT(*) as count FROM websites WHERE is_active = 1")
            total_websites = cursor.fetchone()['count']
            
            # Total questions analyzed
            cursor.execute("SELECT COUNT(*) as count FROM analysis_results")
            total_analyses = cursor.fetchone()['count']
            
            # Total misrepresentations
            cursor.execute("SELECT COUNT(*) as count FROM analysis_results WHERE misrepresentation_detected = 1")
            total_misrepresentations = cursor.fetchone()['count']
            
            # Recent activity (last 24 hours)
            cursor.execute('''
                SELECT COUNT(*) as count FROM analysis_results 
                WHERE analyzed_at > datetime('now', '-1 day')
            ''')
            recent_activity = cursor.fetchone()['count']
            
            # Average accuracy score
            cursor.execute("SELECT AVG(accuracy_score) as avg_score FROM analysis_results")
            avg_accuracy = cursor.fetchone()['avg_score'] or 0.0
            
        stats = {
            'total_websites': total_websites,
            'total_analyses': total_analyses,
            'total_misrepresentations': total_misrepresentations,
            'recent_activity': recent_activity,
            'average_accuracy': round(avg_accuracy, 3),
            'misrepresentation_rate': round((total_misrepresentations / max(total_analyses, 1)) * 100, 2)
        }
        
        return stats
    except Exception as e:
        print(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files for React frontend
@app.get("/app/{path:path}")
async def serve_frontend(path: str):
    """Serve React frontend files"""
    frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/build")
    
    if path == "" or path == "/":
        return FileResponse(os.path.join(frontend_path, "index.html"))
    
    file_path = os.path.join(frontend_path, path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        # Return index.html for client-side routing
        return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    
    print("Starting LLM Monitoring System API server...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 54943))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"Server will run on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )



