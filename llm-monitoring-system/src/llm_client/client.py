

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI
import httpx
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.base_url = os.getenv("LITELLM_BASE_URL")
        self.api_key = os.getenv("LITELLM_API_KEY")
        self.model = os.getenv("LITELLM_MODEL")
        
        print(f"Initializing LLM Client with base URL: {self.base_url}")
        print(f"Using model: {self.model}")
        
        # Initialize OpenAI client with custom base URL
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def query_llm(self, question: str, context: str = "") -> Dict:
        """Query the LLM service with a question"""
        print(f"Querying LLM with question: {question[:100]}...")
        
        try:
            prompt = f"""
You are being asked about a governmental organization. Please provide accurate information based on your knowledge.

Question: {question}

{f"Additional context: {context}" if context else ""}

Please provide a clear, factual response.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            result = {
                "response": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "success": True
            }
            
            print(f"LLM response received: {len(result['response'])} characters")
            return result
            
        except Exception as e:
            print(f"Error querying LLM: {str(e)}")
            return {
                "response": "",
                "error": str(e),
                "success": False
            }

    def analyze_accuracy(self, llm_response: str, actual_content: str, question: str) -> Dict:
        """Analyze the accuracy of LLM response against actual website content"""
        print(f"Analyzing accuracy for question: {question[:50]}...")
        
        try:
            analysis_prompt = f"""
You are an expert fact-checker analyzing whether an LLM's response accurately represents information from an official government website.

QUESTION ASKED: {question}

LLM'S RESPONSE: {llm_response}

ACTUAL WEBSITE CONTENT: {actual_content[:3000]}

Please analyze:
1. Is the LLM's response factually accurate based on the website content?
2. Are there any misrepresentations, omissions, or inaccuracies?
3. Rate the accuracy on a scale of 0.0 to 1.0 (where 1.0 is perfectly accurate)
4. Is there evidence of misrepresentation? (Yes/No)

Provide your analysis in the following JSON format:
{{
    "accuracy_score": 0.85,
    "misrepresentation_detected": false,
    "analysis_summary": "Brief summary of your analysis",
    "specific_issues": ["List any specific issues found"],
    "confidence": 0.9
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=800,
                temperature=0.1
            )
            
            analysis_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Look for JSON in the response
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = analysis_text[start_idx:end_idx]
                    analysis_result = json.loads(json_str)
                else:
                    # Fallback if no JSON found
                    analysis_result = {
                        "accuracy_score": 0.5,
                        "misrepresentation_detected": "misrepresentation" in analysis_text.lower(),
                        "analysis_summary": analysis_text[:500],
                        "specific_issues": [],
                        "confidence": 0.5
                    }
                    
            except json.JSONDecodeError:
                print("Failed to parse JSON from analysis response, using fallback")
                analysis_result = {
                    "accuracy_score": 0.5,
                    "misrepresentation_detected": "inaccurate" in analysis_text.lower() or "misrepresentation" in analysis_text.lower(),
                    "analysis_summary": analysis_text[:500],
                    "specific_issues": [],
                    "confidence": 0.5
                }
            
            analysis_result["raw_analysis"] = analysis_text
            analysis_result["success"] = True
            
            print(f"Analysis completed. Accuracy score: {analysis_result.get('accuracy_score', 'N/A')}")
            print(f"Misrepresentation detected: {analysis_result.get('misrepresentation_detected', 'N/A')}")
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in accuracy analysis: {str(e)}")
            return {
                "accuracy_score": 0.0,
                "misrepresentation_detected": True,
                "analysis_summary": f"Analysis failed: {str(e)}",
                "specific_issues": [f"Analysis error: {str(e)}"],
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }

    def generate_questions(self, website_content: str, website_name: str, num_questions: int = 5) -> List[str]:
        """Generate relevant questions based on website content"""
        print(f"Generating {num_questions} questions for {website_name}")
        
        try:
            prompt = f"""
Based on the following content from the government website "{website_name}", generate {num_questions} specific, factual questions that would test whether an LLM accurately represents the information on this website.

Website Content: {website_content[:2000]}

Generate questions that:
1. Ask about specific facts, policies, or statements mentioned on the website
2. Could reveal misrepresentations if answered incorrectly
3. Are clear and specific
4. Cover different aspects of the content

Return only the questions, one per line, numbered 1-{num_questions}.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            questions_text = response.choices[0].message.content
            
            # Parse questions from the response
            questions = []
            for line in questions_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering and clean up
                    question = line.split('.', 1)[-1].strip()
                    question = question.lstrip('- ').strip()
                    if question and question.endswith('?'):
                        questions.append(question)
            
            print(f"Generated {len(questions)} questions")
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return [
                f"What is the main purpose of {website_name}?",
                f"What services does {website_name} provide?",
                f"Who is the current leadership of {website_name}?",
                f"What are the key policies mentioned on {website_name}?",
                f"How can citizens contact {website_name}?"
            ]

    def test_connection(self) -> bool:
        """Test connection to the LLM service"""
        print("Testing LLM connection...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello, please respond with 'Connection successful'"}
                ],
                max_tokens=50
            )
            
            result = "connection successful" in response.choices[0].message.content.lower()
            print(f"Connection test result: {'Success' if result else 'Failed'}")
            return result
            
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False


