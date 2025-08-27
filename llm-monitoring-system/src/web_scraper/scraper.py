

import requests
from bs4 import BeautifulSoup
import hashlib
from typing import Dict, Optional, List
import time
from urllib.parse import urljoin, urlparse
import re

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        print("Web scraper initialized")

    def scrape_website(self, url: str) -> Dict:
        """Scrape a website and extract relevant content"""
        print(f"Scraping website: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title found"
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract main content
            content_selectors = [
                'main', 'article', '.content', '#content', 
                '.main-content', '#main-content', '.post-content',
                '.entry-content', 'section'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body')
            
            if main_content:
                # Extract text content
                text_content = main_content.get_text()
                
                # Clean up the text
                text_content = re.sub(r'\s+', ' ', text_content)
                text_content = text_content.strip()
                
                # Extract important sections
                headings = []
                for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    heading_text = heading.get_text().strip()
                    if heading_text:
                        headings.append(heading_text)
                
                # Extract paragraphs
                paragraphs = []
                for p in main_content.find_all('p'):
                    p_text = p.get_text().strip()
                    if len(p_text) > 20:  # Only include substantial paragraphs
                        paragraphs.append(p_text)
                
                # Create content hash for change detection
                content_hash = hashlib.md5(text_content.encode()).hexdigest()
                
                result = {
                    'url': url,
                    'title': title_text,
                    'content': text_content[:10000],  # Limit content size
                    'headings': headings[:20],  # Limit headings
                    'paragraphs': paragraphs[:50],  # Limit paragraphs
                    'content_hash': content_hash,
                    'scraped_at': time.time(),
                    'success': True,
                    'status_code': response.status_code,
                    'content_length': len(text_content)
                }
                
                print(f"Successfully scraped {url}")
                print(f"Title: {title_text}")
                print(f"Content length: {len(text_content)} characters")
                print(f"Found {len(headings)} headings and {len(paragraphs)} paragraphs")
                
                return result
                
            else:
                print(f"No main content found for {url}")
                return {
                    'url': url,
                    'title': title_text,
                    'content': '',
                    'headings': [],
                    'paragraphs': [],
                    'content_hash': '',
                    'success': False,
                    'error': 'No main content found'
                }
                
        except requests.RequestException as e:
            print(f"Request error scraping {url}: {str(e)}")
            return {
                'url': url,
                'success': False,
                'error': f"Request error: {str(e)}"
            }
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'success': False,
                'error': f"Scraping error: {str(e)}"
            }

    def extract_key_information(self, content: str) -> Dict:
        """Extract key information from scraped content"""
        print("Extracting key information from content...")
        
        # Look for common government website patterns
        key_info = {
            'leadership': [],
            'policies': [],
            'services': [],
            'contact_info': [],
            'announcements': [],
            'dates': []
        }
        
        content_lower = content.lower()
        
        # Extract leadership information
        leadership_patterns = [
            r'president\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'director\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'secretary\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'administrator\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'chief\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in leadership_patterns:
            matches = re.findall(pattern, content)
            key_info['leadership'].extend(matches)
        
        # Extract dates
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            key_info['dates'].extend(matches)
        
        # Extract email addresses and phone numbers
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        key_info['contact_info'].extend(re.findall(email_pattern, content))
        key_info['contact_info'].extend(re.findall(phone_pattern, content))
        
        # Look for policy-related keywords
        policy_keywords = ['policy', 'regulation', 'law', 'act', 'bill', 'statute', 'rule']
        for keyword in policy_keywords:
            if keyword in content_lower:
                # Extract sentences containing policy keywords
                sentences = content.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower() and len(sentence.strip()) > 20:
                        key_info['policies'].append(sentence.strip())
                        if len(key_info['policies']) >= 5:
                            break
        
        # Look for service-related information
        service_keywords = ['service', 'program', 'benefit', 'assistance', 'support', 'help']
        for keyword in service_keywords:
            if keyword in content_lower:
                sentences = content.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower() and len(sentence.strip()) > 20:
                        key_info['services'].append(sentence.strip())
                        if len(key_info['services']) >= 5:
                            break
        
        # Remove duplicates and limit results
        for key in key_info:
            key_info[key] = list(set(key_info[key]))[:10]
        
        print(f"Extracted key information:")
        for key, values in key_info.items():
            if values:
                print(f"  {key}: {len(values)} items")
        
        return key_info

    def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible"""
        print(f"Validating URL: {url}")
        
        try:
            response = self.session.head(url, timeout=10)
            is_valid = response.status_code < 400
            print(f"URL validation result: {'Valid' if is_valid else 'Invalid'} (Status: {response.status_code})")
            return is_valid
        except Exception as e:
            print(f"URL validation failed: {str(e)}")
            return False

    def get_page_links(self, url: str, same_domain_only: bool = True) -> List[str]:
        """Extract links from a webpage"""
        print(f"Extracting links from: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            base_domain = urlparse(url).netloc
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Skip non-HTTP links
                if not full_url.startswith(('http://', 'https://')):
                    continue
                
                # Check domain restriction
                if same_domain_only:
                    link_domain = urlparse(full_url).netloc
                    if link_domain != base_domain:
                        continue
                
                # Skip common non-content links
                skip_patterns = [
                    r'\.pdf$', r'\.doc$', r'\.zip$', r'\.jpg$', r'\.png$', r'\.gif$',
                    r'/login', r'/logout', r'/admin', r'/search', r'#'
                ]
                
                should_skip = False
                for pattern in skip_patterns:
                    if re.search(pattern, full_url, re.IGNORECASE):
                        should_skip = True
                        break
                
                if not should_skip and full_url not in links:
                    links.append(full_url)
            
            print(f"Found {len(links)} valid links")
            return links[:50]  # Limit to 50 links
            
        except Exception as e:
            print(f"Error extracting links from {url}: {str(e)}")
            return []


