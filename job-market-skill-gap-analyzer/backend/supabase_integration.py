"""
Integration script for Supabase.
Handles database setup and data synchronization.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database import FileStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()


class SupabaseIntegration:
    """Manages Supabase integration and data sync."""
    
    def __init__(self):
        """Initialize Supabase client."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            logger.warning("Supabase credentials not found. Using file storage fallback.")
            self.client = None
            self.storage = FileStorage()
        else:
            self.client: Client = create_client(url, key)
            logger.info("Supabase client initialized")
    
    def sync_jobs_to_supabase(self, jobs_df: pd.DataFrame):
        """
        Sync job data to Supabase.
        
        Args:
            jobs_df: DataFrame with job data
        """
        if not self.client:
            logger.warning("Supabase not configured. Saving to file storage.")
            self.storage.save_jobs(jobs_df)
            return
        
        try:
            # Convert DataFrame to records
            records = jobs_df.to_dict('records')
            
            # Batch insert/upsert
            for record in records:
                # Convert lists to JSON-compatible format
                if 'skills' in record and isinstance(record['skills'], list):
                    record['skills'] = record['skills']
                
                self.client.table('jobs').upsert(record, on_conflict='job_id').execute()
            
            logger.info(f"Synced {len(records)} jobs to Supabase")
        
        except Exception as e:
            logger.error(f"Error syncing jobs to Supabase: {e}")
            logger.info("Falling back to file storage")
            self.storage.save_jobs(jobs_df)
    
    def sync_skill_demand_to_supabase(self, demand_df: pd.DataFrame):
        """
        Sync skill demand data to Supabase.
        
        Args:
            demand_df: DataFrame with skill demand statistics
        """
        if not self.client:
            logger.warning("Supabase not configured. Saving to file storage.")
            self.storage.save_skill_demand(demand_df)
            return
        
        try:
            records = demand_df.to_dict('records')
            
            for record in records:
                self.client.table('skill_demand').upsert(record, on_conflict='skill').execute()
            
            logger.info(f"Synced {len(records)} skill demand records to Supabase")
        
        except Exception as e:
            logger.error(f"Error syncing skill demand to Supabase: {e}")
            logger.info("Falling back to file storage")
            self.storage.save_skill_demand(demand_df)
    
    def get_skill_demand_from_supabase(self, top_n: int = 50) -> pd.DataFrame:
        """
        Retrieve skill demand from Supabase.
        
        Args:
            top_n: Number of top skills to retrieve
            
        Returns:
            DataFrame with skill demand data
        """
        if not self.client:
            return self.storage.load_skill_demand()
        
        try:
            response = self.client.table('skill_demand') \
                .select('*') \
                .order('job_count', desc=True) \
                .limit(top_n) \
                .execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Error retrieving from Supabase: {e}")
            return self.storage.load_skill_demand()
    
    def save_student_analysis(self, analysis_data: dict):
        """
        Save student analysis to Supabase.
        
        Args:
            analysis_data: Dictionary with analysis results
        """
        if not self.client:
            logger.warning("Supabase not configured. Analysis not saved.")
            return
        
        try:
            self.client.table('student_analysis').insert(analysis_data).execute()
            logger.info("Student analysis saved to Supabase")
        
        except Exception as e:
            logger.error(f"Error saving student analysis: {e}")


def setup_database():
    """Setup database schema."""
    logger.info("Setting up database...")
    
    integration = SupabaseIntegration()
    
    if integration.client:
        logger.info("✓ Supabase connected")
        logger.info("Please run the schema.sql file in your Supabase SQL editor")
        logger.info("Schema file: backend/schema.sql")
    else:
        logger.info("Using file storage (data/processed/)")
        logger.info("To enable Supabase, set SUPABASE_URL and SUPABASE_KEY in .env")


if __name__ == "__main__":
    setup_database()
