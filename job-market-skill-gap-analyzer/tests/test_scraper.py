"""
Unit tests for scraping module.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraping.scraper import JobScraper


class TestJobScraper:
    """Test cases for JobScraper class."""
    
    @pytest.fixture
    def scraper(self, tmp_path):
        """Create a scraper instance with temporary output directory."""
        return JobScraper(output_dir=str(tmp_path))
    
    def test_scraper_initialization(self, scraper):
        """Test scraper initializes correctly."""
        assert scraper is not None
        assert scraper.output_dir.exists()
    
    def test_generate_sample_jobs(self, scraper):
        """Test sample job generation."""
        jobs = scraper._generate_sample_jobs(count=10)
        
        assert len(jobs) == 10
        assert all('job_id' in job for job in jobs)
        assert all('title' in job for job in jobs)
        assert all('company' in job for job in jobs)
        assert all('description' in job for job in jobs)
    
    def test_scrape_jobs(self, scraper):
        """Test scraping/generating jobs."""
        jobs_df = scraper.scrape_jobs(
            keywords=["data scientist"],
            locations=["Remote"],
            max_jobs=20
        )
        
        assert isinstance(jobs_df, pd.DataFrame)
        assert len(jobs_df) > 0
        assert 'title' in jobs_df.columns
        assert 'description' in jobs_df.columns
    
    def test_save_jobs(self, scraper, tmp_path):
        """Test saving jobs to file."""
        jobs_df = pd.DataFrame({
            'job_id': ['JOB_001', 'JOB_002'],
            'title': ['Data Scientist', 'Data Engineer'],
            'company': ['Company A', 'Company B'],
            'description': ['Description 1', 'Description 2']
        })
        
        filepath = scraper.save_jobs(jobs_df, filename="test_jobs.csv")
        
        assert filepath.exists()
        assert filepath.suffix == '.csv'
        
        # Verify content
        loaded_df = pd.read_csv(filepath)
        assert len(loaded_df) == 2
        assert list(loaded_df['title']) == ['Data Scientist', 'Data Engineer']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
