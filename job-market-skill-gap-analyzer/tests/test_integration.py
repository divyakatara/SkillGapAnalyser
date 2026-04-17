"""
Integration test - complete pipeline execution.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraping.scraper import JobScraper
from nlp.skill_extractor import SkillExtractor


@pytest.mark.integration
class TestIntegration:
    """Integration tests for complete pipeline."""
    
    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Create temporary data directory."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return data_dir
    
    def test_complete_pipeline(self, temp_data_dir):
        """Test complete pipeline from scraping to analysis."""
        
        # Step 1: Scrape jobs
        scraper = JobScraper(output_dir=str(temp_data_dir))
        jobs_df = scraper.scrape_jobs(
            keywords=["data scientist"],
            locations=["Remote"],
            max_jobs=20
        )
        
        assert len(jobs_df) > 0
        
        # Step 2: Extract skills
        extractor = SkillExtractor()
        jobs_with_skills = extractor.extract_skills_from_jobs(jobs_df)
        
        assert 'skills' in jobs_with_skills.columns
        assert jobs_with_skills['skills'].apply(len).sum() > 0
        
        # Step 3: Compute demand
        demand_df = extractor.compute_skill_demand(jobs_with_skills)
        
        assert len(demand_df) > 0
        assert 'skill' in demand_df.columns
        assert 'percentage' in demand_df.columns
        
        # Step 4: Analyze resume
        resume_text = "Experienced in Python, SQL, and Machine Learning"
        resume_data = extractor.extract_from_resume(resume_text)
        
        assert len(resume_data['skills']) > 0
        
        # Step 5: Compare skills
        gap_df = extractor.compare_skills(
            student_skills=resume_data['skills'],
            market_demand=demand_df,
            top_n=20
        )
        
        assert len(gap_df) > 0
        assert 'student_has' in gap_df.columns
        assert 'gap' in gap_df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
