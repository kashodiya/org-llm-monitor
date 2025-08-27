


import time
import schedule
from datetime import datetime
from typing import List, Dict
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

from ..database.models import DatabaseManager
from ..web_scraper.scraper import WebScraper
from ..llm_client.client import LLMClient

class MonitoringSystem:
    def __init__(self):
        self.db = DatabaseManager()
        self.scraper = WebScraper()
        self.llm_client = LLMClient()
        self.is_running = False
        self.current_session_id = None
        
        print("Monitoring system initialized")

    def start_monitoring_session(self, session_name: str = None) -> int:
        """Start a new monitoring session"""
        if not session_name:
            session_name = f"Monitoring Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        print(f"Starting monitoring session: {session_name}")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO monitoring_sessions (session_name, started_at, status)
                VALUES (?, ?, 'running')
            ''', (session_name, datetime.now()))
            session_id = cursor.lastrowid
            conn.commit()
        
        self.current_session_id = session_id
        print(f"Monitoring session started with ID: {session_id}")
        return session_id

    def complete_monitoring_session(self, session_id: int, total_questions: int, misrepresentations_found: int):
        """Complete a monitoring session"""
        print(f"Completing monitoring session {session_id}")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE monitoring_sessions 
                SET completed_at = ?, status = 'completed', 
                    total_questions = ?, misrepresentations_found = ?
                WHERE id = ?
            ''', (datetime.now(), total_questions, misrepresentations_found, session_id))
            conn.commit()
        
        print(f"Session {session_id} completed. Questions: {total_questions}, Misrepresentations: {misrepresentations_found}")

    def monitor_website(self, website_id: int) -> Dict:
        """Monitor a single website"""
        print(f"Monitoring website ID: {website_id}")
        
        # Get website details
        websites = self.db.get_websites()
        website = next((w for w in websites if w['id'] == website_id), None)
        
        if not website:
            print(f"Website with ID {website_id} not found")
            return {'success': False, 'error': 'Website not found'}
        
        print(f"Monitoring website: {website['name']} ({website['url']})")
        
        results = {
            'website_id': website_id,
            'website_name': website['name'],
            'website_url': website['url'],
            'scraping_success': False,
            'questions_generated': 0,
            'questions_analyzed': 0,
            'misrepresentations_found': 0,
            'errors': []
        }
        
        try:
            # Step 1: Scrape website content
            print("Step 1: Scraping website content...")
            scrape_result = self.scraper.scrape_website(website['url'])
            
            if not scrape_result.get('success', False):
                error_msg = f"Failed to scrape website: {scrape_result.get('error', 'Unknown error')}"
                print(error_msg)
                results['errors'].append(error_msg)
                return results
            
            results['scraping_success'] = True
            
            # Store scraped content
            content_id = self.db.add_website_content(
                website_id=website_id,
                title=scrape_result['title'],
                content=scrape_result['content'],
                content_hash=scrape_result['content_hash']
            )
            
            # Step 2: Generate questions based on content
            print("Step 2: Generating questions...")
            questions = self.llm_client.generate_questions(
                website_content=scrape_result['content'],
                website_name=website['name'],
                num_questions=5
            )
            
            results['questions_generated'] = len(questions)
            
            if not questions:
                error_msg = "No questions generated"
                print(error_msg)
                results['errors'].append(error_msg)
                return results
            
            # Step 3: Process each question
            print(f"Step 3: Processing {len(questions)} questions...")
            
            for i, question in enumerate(questions, 1):
                print(f"Processing question {i}/{len(questions)}: {question[:50]}...")
                
                try:
                    # Add question to database
                    question_id = self.db.add_question(
                        website_id=website_id,
                        question_text=question,
                        category="auto-generated"
                    )
                    
                    # Query LLM with the question
                    llm_response = self.llm_client.query_llm(question)
                    
                    if not llm_response.get('success', False):
                        error_msg = f"LLM query failed for question {i}: {llm_response.get('error', 'Unknown error')}"
                        print(error_msg)
                        results['errors'].append(error_msg)
                        continue
                    
                    # Store LLM response
                    response_id = self.db.add_llm_response(
                        question_id=question_id,
                        llm_service="LiteLLM",
                        response_text=llm_response['response'],
                        metadata=llm_response.get('usage', {})
                    )
                    
                    # Analyze accuracy
                    analysis_result = self.llm_client.analyze_accuracy(
                        llm_response=llm_response['response'],
                        actual_content=scrape_result['content'],
                        question=question
                    )
                    
                    if analysis_result.get('success', False):
                        # Store analysis result
                        self.db.add_analysis_result(
                            llm_response_id=response_id,
                            website_content_id=content_id,
                            accuracy_score=analysis_result.get('accuracy_score', 0.0),
                            misrepresentation_detected=analysis_result.get('misrepresentation_detected', False),
                            analysis_details=str(analysis_result)
                        )
                        
                        results['questions_analyzed'] += 1
                        
                        if analysis_result.get('misrepresentation_detected', False):
                            results['misrepresentations_found'] += 1
                            print(f"⚠️  Misrepresentation detected for question: {question[:50]}...")
                    else:
                        error_msg = f"Analysis failed for question {i}: {analysis_result.get('error', 'Unknown error')}"
                        print(error_msg)
                        results['errors'].append(error_msg)
                    
                    # Small delay between questions
                    time.sleep(1)
                    
                except Exception as e:
                    error_msg = f"Error processing question {i}: {str(e)}"
                    print(error_msg)
                    results['errors'].append(error_msg)
                    continue
            
            print(f"Website monitoring completed for {website['name']}")
            print(f"Questions analyzed: {results['questions_analyzed']}")
            print(f"Misrepresentations found: {results['misrepresentations_found']}")
            
            results['success'] = True
            return results
            
        except Exception as e:
            error_msg = f"Error monitoring website {website_id}: {str(e)}"
            print(error_msg)
            results['errors'].append(error_msg)
            results['success'] = False
            return results

    def monitor_all_websites(self) -> Dict:
        """Monitor all active websites"""
        print("Starting monitoring of all websites...")
        
        session_id = self.start_monitoring_session()
        
        websites = self.db.get_websites(active_only=True)
        
        if not websites:
            print("No active websites found to monitor")
            return {'success': False, 'error': 'No active websites found'}
        
        print(f"Found {len(websites)} websites to monitor")
        
        overall_results = {
            'session_id': session_id,
            'total_websites': len(websites),
            'websites_processed': 0,
            'total_questions': 0,
            'total_misrepresentations': 0,
            'website_results': [],
            'errors': []
        }
        
        # Monitor each website
        for website in websites:
            print(f"\n{'='*50}")
            print(f"Monitoring website: {website['name']}")
            print(f"{'='*50}")
            
            try:
                result = self.monitor_website(website['id'])
                overall_results['website_results'].append(result)
                
                if result.get('success', False):
                    overall_results['websites_processed'] += 1
                    overall_results['total_questions'] += result.get('questions_analyzed', 0)
                    overall_results['total_misrepresentations'] += result.get('misrepresentations_found', 0)
                
                overall_results['errors'].extend(result.get('errors', []))
                
            except Exception as e:
                error_msg = f"Failed to monitor website {website['name']}: {str(e)}"
                print(error_msg)
                overall_results['errors'].append(error_msg)
        
        # Complete the monitoring session
        self.complete_monitoring_session(
            session_id=session_id,
            total_questions=overall_results['total_questions'],
            misrepresentations_found=overall_results['total_misrepresentations']
        )
        
        print(f"\n{'='*50}")
        print("MONITORING SUMMARY")
        print(f"{'='*50}")
        print(f"Websites processed: {overall_results['websites_processed']}/{overall_results['total_websites']}")
        print(f"Total questions analyzed: {overall_results['total_questions']}")
        print(f"Total misrepresentations found: {overall_results['total_misrepresentations']}")
        print(f"Total errors: {len(overall_results['errors'])}")
        
        overall_results['success'] = True
        return overall_results

    def add_website_to_monitor(self, url: str, name: str, description: str = "") -> int:
        """Add a new website to monitor"""
        print(f"Adding website to monitoring: {name} ({url})")
        
        # Validate URL first
        if not self.scraper.validate_url(url):
            raise ValueError(f"URL is not accessible: {url}")
        
        website_id = self.db.add_website(url, name, description)
        print(f"Website added successfully with ID: {website_id}")
        
        return website_id

    def setup_scheduled_monitoring(self, interval_hours: int = 6):
        """Setup scheduled monitoring"""
        print(f"Setting up scheduled monitoring every {interval_hours} hours")
        
        schedule.clear()
        schedule.every(interval_hours).hours.do(self.monitor_all_websites)
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.is_running = True
        self.scheduler_thread.start()
        
        print("Scheduled monitoring started")

    def stop_scheduled_monitoring(self):
        """Stop scheduled monitoring"""
        print("Stopping scheduled monitoring...")
        self.is_running = False
        schedule.clear()
        print("Scheduled monitoring stopped")

    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'current_session_id': self.current_session_id,
            'scheduled_jobs': len(schedule.jobs),
            'active_websites': len(self.db.get_websites(active_only=True))
        }

    def test_system_components(self) -> Dict:
        """Test all system components"""
        print("Testing system components...")
        
        results = {
            'database': False,
            'llm_client': False,
            'web_scraper': False,
            'overall': False
        }
        
        try:
            # Test database
            websites = self.db.get_websites()
            results['database'] = True
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database test failed: {str(e)}")
        
        try:
            # Test LLM client
            results['llm_client'] = self.llm_client.test_connection()
            if results['llm_client']:
                print("✅ LLM client connection successful")
            else:
                print("❌ LLM client test failed")
        except Exception as e:
            print(f"❌ LLM client test failed: {str(e)}")
        
        try:
            # Test web scraper
            test_result = self.scraper.validate_url("https://www.google.com")
            results['web_scraper'] = test_result
            if results['web_scraper']:
                print("✅ Web scraper test successful")
            else:
                print("❌ Web scraper test failed")
        except Exception as e:
            print(f"❌ Web scraper test failed: {str(e)}")
        
        results['overall'] = all(results.values())
        
        print(f"Overall system test: {'✅ PASSED' if results['overall'] else '❌ FAILED'}")
        return results



