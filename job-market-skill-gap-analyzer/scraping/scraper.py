"""
Job scraper for collecting job postings from various sources.
Supports fallback to sample data generation if scraping is blocked.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobScraper:
    """Scrapes job postings or generates sample data as fallback."""
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def scrape_jobs(self, keywords: List[str], locations: List[str], max_jobs: int = 100) -> pd.DataFrame:
        """
        Attempt to scrape job postings. Falls back to sample data if scraping fails.
        
        Args:
            keywords: Job search keywords
            locations: Job locations
            max_jobs: Maximum number of jobs to collect
            
        Returns:
            DataFrame with job postings
        """
        logger.info(f"Starting job collection for keywords: {keywords}")
        
        # Try scraping (will typically fail due to anti-scraping measures)
        jobs = self._try_scraping(keywords, locations, max_jobs)
        
        # Fallback to generating realistic sample data
        if not jobs or len(jobs) < 10:
            logger.warning("Scraping failed or insufficient data. Generating sample dataset.")
            jobs = self._generate_sample_jobs(max_jobs)
        
        df = pd.DataFrame(jobs)
        logger.info(f"Collected {len(df)} job postings")
        
        return df
    
    def _try_scraping(self, keywords: List[str], locations: List[str], max_jobs: int) -> List[Dict]:
        """Attempt to scrape jobs from public sources."""
        jobs = []
        
        # Note: Most job boards have anti-scraping measures
        # This is a placeholder that demonstrates the structure
        # In production, you would use official APIs where available
        
        try:
            # Example: Try a simple search (likely to be blocked)
            for keyword in keywords[:1]:  # Limit attempts
                url = f"https://www.indeed.com/jobs?q={keyword.replace(' ', '+')}&l=remote"
                
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Parse jobs (structure varies by site)
                    # This is simplified and likely won't work due to anti-scraping
                    job_cards = soup.find_all('div', class_='job_seen_beacon')[:5]
                    
                    for card in job_cards:
                        try:
                            jobs.append({
                                'title': card.find('h2').text.strip(),
                                'company': card.find('span', class_='companyName').text.strip(),
                                'location': 'Remote',
                                'description': card.text[:500],
                                'date_posted': datetime.now().strftime('%Y-%m-%d'),
                                'source': 'indeed'
                            })
                        except:
                            continue
                
                time.sleep(2)  # Rate limiting
                
        except Exception as e:
            logger.warning(f"Scraping attempt failed: {e}")
        
        return jobs
    
    def _generate_sample_jobs(self, count: int = 100) -> List[Dict]:
        """Generate realistic sample job postings for development and testing."""
        
        # Realistic job titles
        titles = [
            "Data Scientist",
            "Senior Data Scientist",
            "Machine Learning Engineer",
            "Data Engineer",
            "Senior Data Engineer",
            "ML Engineer",
            "AI Research Scientist",
            "Data Analyst",
            "Business Intelligence Engineer",
            "Analytics Engineer",
            "MLOps Engineer",
            "Deep Learning Engineer",
            "NLP Engineer",
            "Computer Vision Engineer",
            "Staff Data Scientist"
        ]
        
        # Company names
        companies = [
            "Google", "Meta", "Amazon", "Microsoft", "Apple",
            "Netflix", "Uber", "Airbnb", "Spotify", "Tesla",
            "NVIDIA", "OpenAI", "Anthropic", "DataBricks", "Snowflake",
            "MongoDB", "Stripe", "Square", "Coinbase", "Reddit",
            "Twitter", "LinkedIn", "Salesforce", "Adobe", "Oracle",
            "IBM", "Intel", "AMD", "Cisco", "VMware"
        ]
        
        # Locations
        locations = [
            "San Francisco, CA", "New York, NY", "Seattle, WA",
            "Austin, TX", "Boston, MA", "Remote", "Hybrid - Bay Area",
            "Los Angeles, CA", "Chicago, IL", "Denver, CO"
        ]
        
        # Job description templates with skill requirements
        description_templates = [
            """We are seeking a talented {title} to join our data team. 

Key Responsibilities:
- Design and implement machine learning models for production
- Work with large-scale datasets using Python and SQL
- Build data pipelines using Apache Spark and Airflow
- Collaborate with cross-functional teams

Required Skills:
- Python, SQL, Pandas, NumPy
- Machine Learning (scikit-learn, TensorFlow, PyTorch)
- Big Data tools (Spark, Hadoop)
- Cloud platforms (AWS, GCP, or Azure)
- Data visualization (Tableau, PowerBI, or Plotly)
- Statistical analysis and A/B testing
- Git version control

Preferred:
- Experience with Docker and Kubernetes
- Knowledge of MLOps practices
- Strong communication skills""",
            
            """Join our team as a {title}! 

What You'll Do:
- Build scalable data infrastructure
- Develop ML models to solve business problems
- Optimize data processing pipelines
- Create dashboards and reports

Required Qualifications:
- Strong Python programming skills
- Experience with SQL and databases (PostgreSQL, MySQL)
- Proficiency in Pandas, NumPy, scikit-learn
- Experience with AWS or GCP
- Knowledge of Apache Spark and Kafka
- Familiarity with Docker
- Excel, PowerBI or Tableau experience

Nice to Have:
- TensorFlow or PyTorch experience
- Airflow or similar orchestration tools
- Snowflake or BigQuery experience""",
            
            """We're hiring a {title} to drive data-driven decisions.

Responsibilities:
- Analyze complex datasets to extract insights
- Build predictive models using machine learning
- Design ETL pipelines using modern tools
- Present findings to stakeholders

Technical Requirements:
- Python (pandas, numpy, scikit-learn)
- SQL and database design
- PySpark for big data processing
- Cloud platforms (AWS S3, EC2, Lambda)
- Visualization tools (Matplotlib, Seaborn, Plotly)
- Git and CI/CD pipelines
- Statistical modeling and hypothesis testing

Bonus:
- Experience with TensorFlow, Keras, or PyTorch
- Knowledge of NLP or Computer Vision
- Familiarity with Kubernetes and Docker
- dbt, Airflow, or Dagster experience"""
        ]
        
        jobs = []
        for i in range(count):
            title = random.choice(titles)
            template = random.choice(description_templates)
            description = template.format(title=title)
            
            # Add some variation to descriptions
            if random.random() > 0.5:
                description += "\n\nAdditional: Experience with deep learning, NLP, or computer vision is a plus."
            
            if random.random() > 0.6:
                description += "\n\nTools: Jupyter, Git, Jira, Confluence"
            
            date_posted = datetime.now() - timedelta(days=random.randint(1, 30))
            
            jobs.append({
                'job_id': f"JOB_{i+1:04d}",
                'title': title,
                'company': random.choice(companies),
                'location': random.choice(locations),
                'description': description,
                'date_posted': date_posted.strftime('%Y-%m-%d'),
                'salary_min': random.choice([100000, 120000, 140000, 160000, 180000]),
                'salary_max': random.choice([150000, 180000, 200000, 220000, 250000]),
                'source': 'generated'
            })
        
        return jobs
    
    def save_jobs(self, df: pd.DataFrame, filename: str = "jobs.csv"):
        """Save jobs to CSV file."""
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {len(df)} jobs to {filepath}")
        
        # Also save as JSON for flexibility
        json_filepath = self.output_dir / filename.replace('.csv', '.json')
        df.to_json(json_filepath, orient='records', indent=2)
        logger.info(f"Saved JSON to {json_filepath}")
        
        return filepath


def main():
    """Main execution function."""
    scraper = JobScraper()
    
    # Configuration
    keywords = ["data scientist", "data engineer", "machine learning engineer"]
    locations = ["Remote", "United States"]
    max_jobs = 200
    
    # Scrape/generate jobs
    jobs_df = scraper.scrape_jobs(keywords, locations, max_jobs)
    
    # Save results
    scraper.save_jobs(jobs_df)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Job Collection Summary")
    print(f"{'='*60}")
    print(f"Total jobs collected: {len(jobs_df)}")
    print(f"Unique companies: {jobs_df['company'].nunique()}")
    print(f"Unique titles: {jobs_df['title'].nunique()}")
    print(f"\nTop 5 job titles:")
    print(jobs_df['title'].value_counts().head())
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
