
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class DatabaseManager:
    def __init__(self, db_path: str = "./monitoring.db"):
        self.db_path = db_path
        self.init_database()
        print(f"Database initialized at: {db_path}")

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize the database with required tables"""
        print("Initializing database tables...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Websites table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS websites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_scraped TIMESTAMP
                )
            ''')
            
            # Website content table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS website_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website_id INTEGER,
                    content_hash TEXT,
                    title TEXT,
                    content TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (website_id) REFERENCES websites (id)
                )
            ''')
            
            # Questions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website_id INTEGER,
                    question_text TEXT NOT NULL,
                    category TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (website_id) REFERENCES websites (id)
                )
            ''')
            
            # LLM responses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS llm_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER,
                    llm_service TEXT NOT NULL,
                    response_text TEXT,
                    response_metadata TEXT,
                    queried_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_id) REFERENCES questions (id)
                )
            ''')
            
            # Analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    llm_response_id INTEGER,
                    website_content_id INTEGER,
                    accuracy_score REAL,
                    misrepresentation_detected BOOLEAN,
                    analysis_details TEXT,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (llm_response_id) REFERENCES llm_responses (id),
                    FOREIGN KEY (website_content_id) REFERENCES website_content (id)
                )
            ''')
            
            # Monitoring sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'running',
                    total_questions INTEGER DEFAULT 0,
                    misrepresentations_found INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            print("Database tables created successfully")

    def add_website(self, url: str, name: str, description: str = "") -> int:
        """Add a new website to monitor"""
        print(f"Adding website: {name} ({url})")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO websites (url, name, description)
                VALUES (?, ?, ?)
            ''', (url, name, description))
            website_id = cursor.lastrowid
            conn.commit()
            
        print(f"Website added with ID: {website_id}")
        return website_id

    def get_websites(self, active_only: bool = True) -> List[Dict]:
        """Get all websites"""
        print("Fetching websites from database...")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM websites"
            if active_only:
                query += " WHERE is_active = 1"
            
            cursor.execute(query)
            websites = [dict(row) for row in cursor.fetchall()]
            
        print(f"Found {len(websites)} websites")
        return websites

    def add_website_content(self, website_id: int, title: str, content: str, content_hash: str) -> int:
        """Add scraped website content"""
        print(f"Adding content for website ID: {website_id}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO website_content (website_id, title, content, content_hash)
                VALUES (?, ?, ?, ?)
            ''', (website_id, title, content, content_hash))
            content_id = cursor.lastrowid
            conn.commit()
            
        print(f"Content added with ID: {content_id}")
        return content_id

    def add_question(self, website_id: int, question_text: str, category: str = "general") -> int:
        """Add a question for a website"""
        print(f"Adding question for website ID: {website_id}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO questions (website_id, question_text, category)
                VALUES (?, ?, ?)
            ''', (website_id, question_text, category))
            question_id = cursor.lastrowid
            conn.commit()
            
        print(f"Question added with ID: {question_id}")
        return question_id

    def add_llm_response(self, question_id: int, llm_service: str, response_text: str, metadata: Dict = None) -> int:
        """Add LLM response"""
        print(f"Adding LLM response for question ID: {question_id}")
        
        metadata_json = json.dumps(metadata) if metadata else "{}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO llm_responses (question_id, llm_service, response_text, response_metadata)
                VALUES (?, ?, ?, ?)
            ''', (question_id, llm_service, response_text, metadata_json))
            response_id = cursor.lastrowid
            conn.commit()
            
        print(f"LLM response added with ID: {response_id}")
        return response_id

    def add_analysis_result(self, llm_response_id: int, website_content_id: int, 
                          accuracy_score: float, misrepresentation_detected: bool, 
                          analysis_details: str) -> int:
        """Add analysis result"""
        print(f"Adding analysis result for response ID: {llm_response_id}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_results 
                (llm_response_id, website_content_id, accuracy_score, 
                 misrepresentation_detected, analysis_details)
                VALUES (?, ?, ?, ?, ?)
            ''', (llm_response_id, website_content_id, accuracy_score, 
                  misrepresentation_detected, analysis_details))
            analysis_id = cursor.lastrowid
            conn.commit()
            
        print(f"Analysis result added with ID: {analysis_id}")
        return analysis_id

    def get_recent_analysis_results(self, limit: int = 50) -> List[Dict]:
        """Get recent analysis results with joined data"""
        print(f"Fetching recent {limit} analysis results...")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    ar.*,
                    lr.response_text,
                    lr.llm_service,
                    q.question_text,
                    w.name as website_name,
                    w.url as website_url,
                    wc.title as content_title
                FROM analysis_results ar
                JOIN llm_responses lr ON ar.llm_response_id = lr.id
                JOIN questions q ON lr.question_id = q.id
                JOIN websites w ON q.website_id = w.id
                JOIN website_content wc ON ar.website_content_id = wc.id
                ORDER BY ar.analyzed_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = [dict(row) for row in cursor.fetchall()]
            
        print(f"Found {len(results)} analysis results")
        return results

    def get_misrepresentations_summary(self) -> Dict:
        """Get summary of misrepresentations"""
        print("Generating misrepresentations summary...")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Total misrepresentations
            cursor.execute('''
                SELECT COUNT(*) as total_misrepresentations
                FROM analysis_results 
                WHERE misrepresentation_detected = 1
            ''')
            total_misrep = cursor.fetchone()['total_misrepresentations']
            
            # Misrepresentations by website
            cursor.execute('''
                SELECT 
                    w.name,
                    w.url,
                    COUNT(*) as misrepresentation_count
                FROM analysis_results ar
                JOIN llm_responses lr ON ar.llm_response_id = lr.id
                JOIN questions q ON lr.question_id = q.id
                JOIN websites w ON q.website_id = w.id
                WHERE ar.misrepresentation_detected = 1
                GROUP BY w.id, w.name, w.url
                ORDER BY misrepresentation_count DESC
            ''')
            by_website = [dict(row) for row in cursor.fetchall()]
            
            # Recent misrepresentations
            cursor.execute('''
                SELECT 
                    ar.analyzed_at,
                    w.name as website_name,
                    q.question_text,
                    ar.accuracy_score
                FROM analysis_results ar
                JOIN llm_responses lr ON ar.llm_response_id = lr.id
                JOIN questions q ON lr.question_id = q.id
                JOIN websites w ON q.website_id = w.id
                WHERE ar.misrepresentation_detected = 1
                ORDER BY ar.analyzed_at DESC
                LIMIT 10
            ''')
            recent = [dict(row) for row in cursor.fetchall()]
            
        summary = {
            'total_misrepresentations': total_misrep,
            'by_website': by_website,
            'recent_misrepresentations': recent
        }
        
        print(f"Summary generated: {total_misrep} total misrepresentations")
        return summary

