#!/usr/bin/env python3

"""
Seed Data Script for LLM Monitoring System

This script seeds the database with Federal Reserve Bank district websites
for monitoring how LLM services represent these governmental organizations.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import DatabaseManager

def seed_federal_reserve_banks():
    """Seed the database with Federal Reserve Bank district websites"""
    
    print("=" * 60)
    print("SEEDING FEDERAL RESERVE BANK DATA")
    print("=" * 60)
    
    # Initialize database manager
    db = DatabaseManager()
    
    # Federal Reserve Bank districts data
    fed_banks = [
        {
            "name": "1st District (Boston)",
            "url": "https://www.bostonfed.org/",
            "description": "Federal Reserve Bank of Boston - Serves Connecticut (excluding Fairfield County), Maine, Massachusetts, New Hampshire, Rhode Island, and Vermont."
        },
        {
            "name": "2nd District (New York)",
            "url": "https://www.newyorkfed.org/",
            "description": "Federal Reserve Bank of New York - Serves New York State, northern New Jersey, Fairfield County in Connecticut, Puerto Rico, and the U.S. Virgin Islands."
        },
        {
            "name": "3rd District (Philadelphia)",
            "url": "https://www.philadelphiafed.org/",
            "description": "Federal Reserve Bank of Philadelphia - Serves eastern Pennsylvania, southern New Jersey, and Delaware."
        },
        {
            "name": "4th District (Cleveland)",
            "url": "https://www.clevelandfed.org/",
            "description": "Federal Reserve Bank of Cleveland - Serves Ohio, western Pennsylvania, eastern Kentucky, and the northern panhandle of West Virginia."
        },
        {
            "name": "5th District (Richmond)",
            "url": "https://www.richmondfed.org/",
            "description": "Federal Reserve Bank of Richmond - Serves Virginia, Maryland, North Carolina, South Carolina, West Virginia (except the northern panhandle), and the District of Columbia."
        },
        {
            "name": "6th District (Atlanta)",
            "url": "https://www.atlantafed.org/",
            "description": "Federal Reserve Bank of Atlanta - Serves Alabama, Florida, Georgia, and portions of Louisiana, Mississippi, and Tennessee."
        },
        {
            "name": "7th District (Chicago)",
            "url": "https://www.chicagofed.org/",
            "description": "Federal Reserve Bank of Chicago - Serves Iowa and portions of Illinois, Indiana, Michigan, and Wisconsin."
        },
        {
            "name": "8th District (St. Louis)",
            "url": "https://www.stlouisfed.org/",
            "description": "Federal Reserve Bank of St. Louis - Serves Arkansas and portions of Illinois, Indiana, Kentucky, Mississippi, Missouri, and Tennessee."
        },
        {
            "name": "9th District (Minneapolis)",
            "url": "https://www.minneapolisfed.org/",
            "description": "Federal Reserve Bank of Minneapolis - Serves Minnesota, Montana, North Dakota, South Dakota, northwestern Wisconsin, and the Upper Peninsula of Michigan."
        },
        {
            "name": "10th District (Kansas City)",
            "url": "https://www.kansascityfed.org/",
            "description": "Federal Reserve Bank of Kansas City - Serves Colorado, Kansas, Nebraska, Oklahoma, Wyoming, northern New Mexico, and western Missouri."
        },
        {
            "name": "11th District (Dallas)",
            "url": "https://www.dallasfed.org/",
            "description": "Federal Reserve Bank of Dallas - Serves Texas, northern Louisiana, and southern New Mexico."
        },
        {
            "name": "12th District (San Francisco)",
            "url": "https://www.frbsf.org/",
            "description": "Federal Reserve Bank of San Francisco - Serves Alaska, Arizona, California, Hawaii, Idaho, Nevada, Oregon, Utah, Washington, American Samoa, Guam, and the Northern Mariana Islands."
        }
    ]
    
    print(f"Adding {len(fed_banks)} Federal Reserve Bank websites to the database...")
    print()
    
    added_count = 0
    for bank in fed_banks:
        try:
            website_id = db.add_website(
                url=bank["url"],
                name=bank["name"],
                description=bank["description"]
            )
            print(f"✅ Added: {bank['name']}")
            added_count += 1
        except Exception as e:
            print(f"❌ Error adding {bank['name']}: {str(e)}")
    
    print()
    print("=" * 60)
    print(f"SEEDING COMPLETE: {added_count}/{len(fed_banks)} websites added")
    print("=" * 60)
    
    # Display summary of added websites
    websites = db.get_websites()
    print(f"\nTotal websites in database: {len(websites)}")
    print("\nWebsites added:")
    for website in websites:
        print(f"  • {website['name']} - {website['url']}")
    
    return added_count

def add_sample_questions():
    """Add sample questions for monitoring Federal Reserve Banks"""
    
    print("\n" + "=" * 60)
    print("ADDING SAMPLE MONITORING QUESTIONS")
    print("=" * 60)
    
    db = DatabaseManager()
    websites = db.get_websites()
    
    # Sample questions to ask about Federal Reserve Banks
    sample_questions = [
        {
            "text": "What is the primary function of this Federal Reserve Bank?",
            "category": "function"
        },
        {
            "text": "What geographic region does this Federal Reserve Bank serve?",
            "category": "geography"
        },
        {
            "text": "Who is the current president of this Federal Reserve Bank?",
            "category": "leadership"
        },
        {
            "text": "What are the main economic research areas of this Federal Reserve Bank?",
            "category": "research"
        },
        {
            "text": "How does this Federal Reserve Bank contribute to monetary policy?",
            "category": "policy"
        }
    ]
    
    questions_added = 0
    for website in websites:
        print(f"\nAdding questions for: {website['name']}")
        for question in sample_questions:
            try:
                question_id = db.add_question(
                    website_id=website['id'],
                    question_text=question['text'],
                    category=question['category']
                )
                questions_added += 1
            except Exception as e:
                print(f"❌ Error adding question: {str(e)}")
    
    print(f"\n✅ Added {questions_added} questions across all websites")
    return questions_added

def main():
    """Main function to run the seeding process"""
    
    try:
        # Seed Federal Reserve Bank websites
        websites_added = seed_federal_reserve_banks()
        
        # Add sample questions
        questions_added = add_sample_questions()
        
        print(f"\n🎉 Seeding completed successfully!")
        print(f"   • {websites_added} websites added")
        print(f"   • {questions_added} questions added")
        print(f"\nThe database is now ready for LLM monitoring!")
        
    except Exception as e:
        print(f"\n❌ Seeding failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
