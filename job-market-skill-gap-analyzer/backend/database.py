"""
Database module for Supabase/PostgreSQL integration.
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, DateTime, Boolean, Text, MetaData, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations for Supabase/PostgreSQL."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            connection_string: PostgreSQL connection string. If None, reads from env.
        """
        if connection_string is None:
            # Build from environment variables
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "postgres")
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "")
            
            connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        self.engine = create_engine(connection_string, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        
        # Define tables
        self._define_tables()
        
        logger.info("Database manager initialized")
    
    def _define_tables(self):
        """Define database table schemas."""
        
        # Jobs table
        self.jobs_table = Table(
            'jobs',
            self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('job_id', String(100), unique=True, nullable=False),
            Column('title', String(200), nullable=False),
            Column('company', String(200)),
            Column('location', String(200)),
            Column('description', Text),
            Column('date_posted', String(20)),
            Column('salary_min', Integer),
            Column('salary_max', Integer),
            Column('source', String(50)),
            Column('skills', JSON),
            Column('created_at', DateTime, default=datetime.utcnow)
        )
        
        # Skill demand table
        self.skill_demand_table = Table(
            'skill_demand',
            self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('skill', String(100), unique=True, nullable=False),
            Column('job_count', Integer),
            Column('percentage', Float),
            Column('demand_level', String(20)),
            Column('category', String(50)),
            Column('updated_at', DateTime, default=datetime.utcnow)
        )
        
        # Student analysis table
        self.student_analysis_table = Table(
            'student_analysis',
            self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('student_name', String(200)),
            Column('resume_text', Text),
            Column('skills', JSON),
            Column('skill_count', Integer),
            Column('gap_analysis', JSON),
            Column('created_at', DateTime, default=datetime.utcnow)
        )
    
    def create_tables(self):
        """Create all tables if they don't exist."""
        try:
            self.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def insert_jobs(self, jobs_df: pd.DataFrame):
        """
        Insert job postings into database.
        
        Args:
            jobs_df: DataFrame with job data
        """
        try:
            # Convert to dict records
            records = jobs_df.to_dict('records')
            
            with self.engine.connect() as conn:
                for record in records:
                    # Handle upsert (insert or update)
                    stmt = insert(self.jobs_table).values(record)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['job_id'],
                        set_=dict(
                            title=stmt.excluded.title,
                            company=stmt.excluded.company,
                            location=stmt.excluded.location,
                            description=stmt.excluded.description,
                            skills=stmt.excluded.skills
                        )
                    )
                    conn.execute(stmt)
                conn.commit()
            
            logger.info(f"Inserted {len(records)} jobs into database")
        except Exception as e:
            logger.error(f"Error inserting jobs: {e}")
            raise
    
    def insert_skill_demand(self, demand_df: pd.DataFrame):
        """
        Insert skill demand data into database.
        
        Args:
            demand_df: DataFrame with skill demand statistics
        """
        try:
            records = demand_df.to_dict('records')
            
            with self.engine.connect() as conn:
                for record in records:
                    record['updated_at'] = datetime.utcnow()
                    stmt = insert(self.skill_demand_table).values(record)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['skill'],
                        set_=dict(
                            job_count=stmt.excluded.job_count,
                            percentage=stmt.excluded.percentage,
                            demand_level=stmt.excluded.demand_level,
                            category=stmt.excluded.category,
                            updated_at=stmt.excluded.updated_at
                        )
                    )
                    conn.execute(stmt)
                conn.commit()
            
            logger.info(f"Inserted {len(records)} skill demand records")
        except Exception as e:
            logger.error(f"Error inserting skill demand: {e}")
            raise
    
    def insert_student_analysis(self, student_data: Dict):
        """
        Insert student analysis into database.
        
        Args:
            student_data: Dictionary with student analysis data
        """
        try:
            student_data['created_at'] = datetime.utcnow()
            
            with self.engine.connect() as conn:
                stmt = insert(self.student_analysis_table).values(student_data)
                conn.execute(stmt)
                conn.commit()
            
            logger.info("Student analysis saved to database")
        except Exception as e:
            logger.error(f"Error inserting student analysis: {e}")
            raise
    
    def get_skill_demand(self, top_n: int = 50) -> pd.DataFrame:
        """
        Retrieve skill demand data.
        
        Args:
            top_n: Number of top skills to retrieve
            
        Returns:
            DataFrame with skill demand data
        """
        query = f"""
        SELECT skill, job_count, percentage, demand_level, category
        FROM skill_demand
        ORDER BY job_count DESC
        LIMIT {top_n}
        """
        
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            logger.error(f"Error retrieving skill demand: {e}")
            return pd.DataFrame()
    
    def get_jobs(self, limit: int = 100) -> pd.DataFrame:
        """
        Retrieve job postings.
        
        Args:
            limit: Maximum number of jobs to retrieve
            
        Returns:
            DataFrame with job data
        """
        query = f"""
        SELECT job_id, title, company, location, date_posted, skills
        FROM jobs
        ORDER BY created_at DESC
        LIMIT {limit}
        """
        
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            logger.error(f"Error retrieving jobs: {e}")
            return pd.DataFrame()


# Fallback: File-based storage if database is not available
class FileStorage:
    """
    File-based storage for job market data.
    Primary data source: India_tech_jobs.xls
    """
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Primary data source - CSV file with Indian tech jobs (despite .xls extension)
        self.data_file = self.storage_dir / "India_tech_jobs.xls"
        
        # Cache directory for processed data
        self.cache_dir = self.storage_dir / "processed"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Using file storage at {storage_dir}")
        logger.info(f"Primary data source: {self.data_file}")
    
    def load_jobs_from_xls(self) -> pd.DataFrame:
        """
        Load jobs from India_tech_jobs.xls file (actually CSV format).
        
        Returns:
            DataFrame with job data
        """
        if not self.data_file.exists():
            logger.error(f"Data file not found: {self.data_file}")
            logger.error("Please ensure India_tech_jobs.xls exists in the data/ directory")
            return pd.DataFrame()
        
        try:
            # File has .xls extension but is actually CSV format
            df = pd.read_csv(self.data_file, encoding='utf-8')
            logger.info(f"Loaded {len(df)} jobs from data file")
            
            # Log available columns
            logger.info(f"Available columns: {list(df.columns)}")
            
            # Ensure required columns exist
            required_columns = ['description']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                return pd.DataFrame()
            
            # Standardize column names
            if 'date_posted' not in df.columns and 'posted_date' in df.columns:
                df = df.rename(columns={'posted_date': 'date_posted'})
            
            # Clean up data - remove rows without descriptions
            df = df.dropna(subset=['description'])
            
            # Remove empty descriptions
            df = df[df['description'].str.strip() != '']
            
            logger.info(f"After cleaning: {len(df)} jobs with valid descriptions")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading data file: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return pd.DataFrame()
    
    def save_jobs(self, jobs_df: pd.DataFrame):
        """Save processed jobs to cache (for performance optimization)."""
        filepath = self.cache_dir / "jobs_cache.csv"
        jobs_df.to_csv(filepath, index=False)
        logger.info(f"Cached {len(jobs_df)} jobs to {filepath}")
    
    def save_skill_demand(self, demand_df: pd.DataFrame):
        """Save computed skill demand to cache."""
        filepath = self.cache_dir / "skill_demand_cache.csv"
        demand_df.to_csv(filepath, index=False)
        logger.info(f"Cached skill demand ({len(demand_df)} skills) to {filepath}")
    
    def load_skill_demand(self) -> pd.DataFrame:
        """
        Load skill demand data from cache for performance optimization.
        Returns cached data if available, empty DataFrame otherwise.
        """
        filepath = self.cache_dir / "skill_demand_cache.csv"
        
        if not filepath.exists():
            logger.warning(f"No cached skill demand found at {filepath}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} skills from cache")
            return df
        except Exception as e:
            logger.error(f"Error loading cached skill demand: {e}")
            return pd.DataFrame()
    
    def load_jobs_with_skills(self) -> pd.DataFrame:
        """
        Load processed jobs with extracted skills from cache.
        Returns cached data if available, empty DataFrame otherwise.
        """
        filepath = self.cache_dir / "jobs_cache.csv"
        
        if not filepath.exists():
            logger.warning(f"No cached jobs found at {filepath}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} jobs with skills from cache")
            return df
        except Exception as e:
            logger.error(f"Error loading cached jobs: {e}")
            return pd.DataFrame()
    
    def load_jobs(self) -> pd.DataFrame:
        """
        Load job postings from primary data source.
        
        Returns:
            DataFrame with job data including descriptions
        """
        return self.load_jobs_from_xls()
    
    def save_resume(self, resume_id: str, data: Dict):
        """
        Save resume data to file storage.
        
        Args:
            resume_id: Unique resume identifier
            data: Resume data dictionary
        """
        import json
        
        resumes_dir = self.data_dir / "resumes"
        resumes_dir.mkdir(exist_ok=True)
        
        filepath = resumes_dir / f"{resume_id}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved resume {resume_id} to {filepath}")
        except Exception as e:
            logger.error(f"Error saving resume: {e}")
            raise
    
    def get_resume(self, resume_id: str) -> Optional[Dict]:
        """
        Retrieve resume data from file storage.
        
        Args:
            resume_id: Unique resume identifier
            
        Returns:
            Resume data dictionary or None if not found
        """
        import json
        
        filepath = self.data_dir / "resumes" / f"{resume_id}.json"
        
        if not filepath.exists():
            logger.warning(f"Resume {resume_id} not found")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded resume {resume_id}")
            return data
        except Exception as e:
            logger.error(f"Error loading resume: {e}")
            return None


from pathlib import Path
