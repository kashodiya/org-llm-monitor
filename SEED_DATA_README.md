
# Seed Data Scripts

This directory contains scripts to seed the LLM Monitoring System database with Federal Reserve Bank data.

## Scripts

### `seed_data.py`
Seeds the database with all 12 Federal Reserve Bank district websites and sample monitoring questions.

**Usage:**
```bash
python3 seed_data.py
```

**What it does:**
- Adds all 12 Federal Reserve Bank district websites to the `websites` table
- Adds 5 sample monitoring questions for each website (60 total questions)
- Creates the database if it doesn't exist
- Provides detailed output of the seeding process

### `verify_seed_data.py`
Verifies that the seeded data was properly added to the database.

**Usage:**
```bash
python3 verify_seed_data.py
```

**What it checks:**
- Confirms all 12 Federal Reserve districts are present
- Verifies question counts per website
- Checks for duplicate URLs
- Validates URL formats (HTTPS)
- Provides a comprehensive database summary

## Federal Reserve Bank Districts

The following Federal Reserve Bank websites are seeded:

1. **1st District (Boston)** - https://www.bostonfed.org/
2. **2nd District (New York)** - https://www.newyorkfed.org/
3. **3rd District (Philadelphia)** - https://www.philadelphiafed.org/
4. **4th District (Cleveland)** - https://www.clevelandfed.org/
5. **5th District (Richmond)** - https://www.richmondfed.org/
6. **6th District (Atlanta)** - https://www.atlantafed.org/
7. **7th District (Chicago)** - https://www.chicagofed.org/
8. **8th District (St. Louis)** - https://www.stlouisfed.org/
9. **9th District (Minneapolis)** - https://www.minneapolisfed.org/
10. **10th District (Kansas City)** - https://www.kansascityfed.org/
11. **11th District (Dallas)** - https://www.dallasfed.org/
12. **12th District (San Francisco)** - https://www.frbsf.org/

## Sample Questions

Each website gets the following 5 monitoring questions:

1. **Function**: "What is the primary function of this Federal Reserve Bank?"
2. **Geography**: "What geographic region does this Federal Reserve Bank serve?"
3. **Leadership**: "Who is the current president of this Federal Reserve Bank?"
4. **Research**: "What are the main economic research areas of this Federal Reserve Bank?"
5. **Policy**: "How does this Federal Reserve Bank contribute to monetary policy?"

## Database Schema

The seeded data populates these tables:

- **`websites`**: Federal Reserve Bank information
- **`questions`**: Monitoring questions for each website

## Running the Scripts

1. Make sure you're in the project root directory:
   ```bash
   cd /workspace/org-llm-monitor
   ```

2. Run the seed script:
   ```bash
   python3 seed_data.py
   ```

3. Verify the data (optional):
   ```bash
   python3 verify_seed_data.py
   ```

## Output

After successful seeding, you should see:
- ✅ 12 websites added
- ✅ 60 questions added (5 per website)
- Database file created at `./monitoring.db`

The system is now ready to monitor how LLM services represent these Federal Reserve Bank websites!

