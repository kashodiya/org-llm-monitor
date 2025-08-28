#!/usr/bin/env python3

"""
Verification Script for Seeded Data

This script verifies that the Federal Reserve Bank data was properly seeded
into the LLM Monitoring System database.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import DatabaseManager

def verify_seeded_data():
    """Verify the seeded data in the database"""
    
    print("=" * 60)
    print("VERIFYING SEEDED DATA")
    print("=" * 60)
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Get all websites
    websites = db.get_websites()
    
    print(f"📊 Database Summary:")
    print(f"   Total websites: {len(websites)}")
    
    # Verify we have all 12 Federal Reserve Banks
    expected_districts = [
        "1st District (Boston)",
        "2nd District (New York)", 
        "3rd District (Philadelphia)",
        "4th District (Cleveland)",
        "5th District (Richmond)",
        "6th District (Atlanta)",
        "7th District (Chicago)",
        "8th District (St. Louis)",
        "9th District (Minneapolis)",
        "10th District (Kansas City)",
        "11th District (Dallas)",
        "12th District (San Francisco)"
    ]
    
    found_districts = [w['name'] for w in websites]
    missing_districts = [d for d in expected_districts if d not in found_districts]
    
    if missing_districts:
        print(f"❌ Missing districts: {missing_districts}")
    else:
        print("✅ All 12 Federal Reserve Districts found")
    
    print(f"\n📋 Websites in database:")
    for i, website in enumerate(websites, 1):
        print(f"   {i:2d}. {website['name']}")
        print(f"       URL: {website['url']}")
        print(f"       Active: {'Yes' if website['is_active'] else 'No'}")
        print(f"       Created: {website['created_at']}")
        print()
    
    # Check questions
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        question_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT w.name, COUNT(q.id) as question_count
            FROM websites w
            LEFT JOIN questions q ON w.id = q.website_id
            GROUP BY w.id, w.name
            ORDER BY w.name
        """)
        questions_per_website = cursor.fetchall()
    
    print(f"❓ Questions Summary:")
    print(f"   Total questions: {question_count}")
    print(f"   Questions per website:")
    for name, count in questions_per_website:
        print(f"     • {name}: {count} questions")
    
    # Verify database integrity
    print(f"\n🔍 Database Integrity Check:")
    
    # Check for duplicate URLs
    urls = [w['url'] for w in websites]
    duplicate_urls = [url for url in set(urls) if urls.count(url) > 1]
    
    if duplicate_urls:
        print(f"❌ Duplicate URLs found: {duplicate_urls}")
    else:
        print("✅ No duplicate URLs")
    
    # Check URL format
    invalid_urls = [w for w in websites if not w['url'].startswith('https://')]
    
    if invalid_urls:
        print(f"❌ Invalid URLs (not HTTPS): {[w['url'] for w in invalid_urls]}")
    else:
        print("✅ All URLs use HTTPS")
    
    print(f"\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    return len(websites) == 12 and question_count == 60

def main():
    """Main verification function"""
    
    try:
        success = verify_seeded_data()
        
        if success:
            print("🎉 All data verified successfully!")
            print("The database is ready for LLM monitoring operations.")
        else:
            print("❌ Data verification failed!")
            print("Please check the seeding process.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
