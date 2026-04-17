#!/usr/bin/env python
"""
Complete pipeline script - runs the entire analysis end-to-end.
"""

import sys
from pathlib import Path
import pandas as pd
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraping.scraper import JobScraper
from nlp.skill_extractor import SkillExtractor
from backend.database import FileStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_pipeline():
    """
    Execute the complete analysis pipeline.
    Loads data from India_tech_jobs.xls and extracts skills from descriptions.
    """
    
    print("\n" + "="*70)
    print("JOB MARKET SKILL GAP ANALYZER - COMPLETE PIPELINE")
    print("="*70 + "\n")
    
    # Initialize components
    storage = FileStorage()
    extractor = SkillExtractor()
    
    # Step 1: Load Data from XLS
    print("STEP 1: Loading Job Data from India_tech_jobs.xls")
    print("-" * 70)
    jobs_df = storage.load_jobs()
    
    if jobs_df.empty:
        print("❌ No data found in data file!")
        print(f"   Expected file: data/India_tech_jobs.xls")
        print("\n   Please ensure the file exists and contains job descriptions.")
        return
    
    print(f"✓ Loaded {len(jobs_df)} job postings")
    print(f"✓ Data source: {storage.data_file}")
    
    # Check required columns
    if 'description' not in jobs_df.columns:
        print("❌ Missing 'description' column in XLS file!")
        print(f"   Available columns: {list(jobs_df.columns)}")
        return
    
    print(f"✓ Valid descriptions found: {jobs_df['description'].notna().sum()}\n")
    
    # Step 2: Extract Skills from Descriptions
    print("STEP 2: Extracting Skills from Job Descriptions")
    print("-" * 70)
    
    jobs_with_skills = extractor.extract_skills_from_jobs(jobs_df)
    
    if jobs_with_skills.empty or 'skills' not in jobs_with_skills.columns:
        print("❌ Failed to extract skills from job descriptions")
        return
    
    # Filter out jobs with no skills
    jobs_with_skills = jobs_with_skills[jobs_with_skills['skill_count'] > 0]
    
    print(f"✓ Extracted skills from {len(jobs_with_skills)} jobs")
    print(f"✓ Average skills per job: {jobs_with_skills['skill_count'].mean():.1f}")
    print(f"✓ Jobs with skills: {len(jobs_with_skills):,}\n")
    
    # Step 3: Skill Demand Analysis
    print("STEP 3: Computing Skill Demand")
    print("-" * 70)
    demand_df = extractor.compute_skill_demand(jobs_with_skills)
    
    if demand_df.empty:
        print("❌ Failed to compute skill demand")
        return
    
    print(f"✓ Found {len(demand_df)} unique skills")
    print(f"✓ Top 5 skills:")
    for idx, row in demand_df.head(5).iterrows():
        print(f"   - {row['skill']}: {row['job_count']} jobs ({row['percentage']:.1f}%)")
    print()
    
    # Step 4: Save Processed Data (Cache)
    print("STEP 4: Caching Processed Data")
    print("-" * 70)
    storage.save_jobs(jobs_with_skills)
    storage.save_skill_demand(demand_df)
    print("✓ Cached processed jobs")
    print("✓ Cached skill demand data")
    print("✓ Cache location: data/processed/\n")
    
    # Step 5: Display Top Skills
    print("STEP 5: Top 20 Skills in Demand")
    print("-" * 70)
    top_20 = demand_df.head(20)
    print(top_20.to_string(index=False))
    print()
    
    # Step 6: Sample Resume Analysis
    print("STEP 6: Sample Resume Analysis")
    print("-" * 70)
    sample_resume = """
    Data Scientist with 3 years of experience
    
    Technical Skills:
    - Python, SQL, R
    - Machine Learning with scikit-learn and TensorFlow
    - Data visualization with Tableau
    - Git version control
    """
    
    resume_data = extractor.extract_from_resume(sample_resume)
    print(f"✓ Extracted {resume_data['skill_count']} skills from sample resume")
    print(f"✓ Skills: {', '.join(resume_data['skills'][:10])}\n")
    
    # Step 7: Gap Analysis
    print("STEP 7: Skill Gap Analysis")
    print("-" * 70)
    gap_df = extractor.compare_skills(
        student_skills=resume_data['skills'],
        market_demand=demand_df,
        top_n=50
    )
    
    matched = gap_df['student_has'].sum()
    missing = (~gap_df['student_has']).sum()
    missing_high = gap_df[(gap_df['gap']) & (gap_df['demand_level'] == 'High')].shape[0]
    
    print(f"✓ Skills matched: {matched}")
    print(f"✓ Skills missing: {missing}")
    print(f"✓ Missing high-demand skills: {missing_high}")
    
    # Top missing skills
    missing_high_demand = gap_df[
        (gap_df['gap']) & (gap_df['demand_level'] == 'High')
    ].head(5)
    
    if not missing_high_demand.empty:
        print("\n🎯 Top 5 Skills to Learn:")
        for _, row in missing_high_demand.iterrows():
            print(f"   • {row['skill']}: {row['percentage']:.1f}% of jobs")
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Launch dashboard: streamlit run frontend/app.py")
    print("2. Start API: python backend/main.py")
    print("3. View data: data/processed/")
    print()


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)
