"""
NLP module for extracting skills from job descriptions and resumes.
Uses spaCy, regex patterns, and a curated skill dictionary.
"""

import re
import json
import spacy
from pathlib import Path
from typing import List, Dict, Set, Tuple
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillExtractor:
    """Extracts skills from text using hybrid NLP approach."""
    
    def __init__(self, skill_dict_path: str = "nlp/skill_dictionary.json"):
        """
        Initialize the skill extractor.
        
        Args:
            skill_dict_path: Path to skill dictionary JSON file
        """
        self.skill_dict_path = Path(skill_dict_path)
        self.skills_by_category = self._load_skill_dictionary()
        self.all_skills = self._flatten_skills()
        
        # Create case-insensitive lookup
        self.skill_lookup = {skill.lower(): skill for skill in self.all_skills}
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model: en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def _load_skill_dictionary(self) -> Dict[str, List[str]]:
        """Load skill dictionary from JSON file."""
        if not self.skill_dict_path.exists():
            logger.error(f"Skill dictionary not found at {self.skill_dict_path}")
            return {}
        
        with open(self.skill_dict_path, 'r', encoding='utf-8') as f:
            skills = json.load(f)
        
        logger.info(f"Loaded {sum(len(v) for v in skills.values())} skills from dictionary")
        return skills
    
    def _flatten_skills(self) -> Set[str]:
        """Create a flat set of all skills."""
        all_skills = set()
        for category_skills in self.skills_by_category.values():
            all_skills.update(category_skills)
        return all_skills
    
    def extract_skills(self, text: str, method: str = "hybrid") -> List[str]:
        """
        Extract skills from text using specified method.
        
        Args:
            text: Input text (job description or resume)
            method: Extraction method - 'hybrid', 'regex', or 'spacy'
            
        Returns:
            List of extracted skills
        """
        if not text:
            return []
        
        if method == "hybrid":
            skills = self._hybrid_extraction(text)
        elif method == "regex":
            skills = self._regex_extraction(text)
        elif method == "spacy":
            skills = self._spacy_extraction(text)
        else:
            raise ValueError(f"Unknown extraction method: {method}")
        
        return sorted(list(set(skills)))
    
    def _hybrid_extraction(self, text: str) -> List[str]:
        """Combine regex and spaCy for robust extraction."""
        regex_skills = self._regex_extraction(text)
        
        if self.nlp:
            spacy_skills = self._spacy_extraction(text)
            combined = set(regex_skills) | set(spacy_skills)
        else:
            combined = set(regex_skills)
        
        return list(combined)
    
    def _regex_extraction(self, text: str) -> List[str]:
        """Extract skills using regex patterns and dictionary matching."""
        extracted_skills = []
        text_lower = text.lower()
        
        # Direct dictionary matching with word boundaries
        for skill in self.all_skills:
            # Create pattern that matches whole words or common variations
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            
            if re.search(pattern, text_lower):
                extracted_skills.append(self.skill_lookup[skill.lower()])
        
        # Special patterns for common skill formats
        
        # Pattern: Python, Java, C++, etc.
        prog_lang_pattern = r'\b(python|java|scala|c\+\+|javascript|typescript|r\b|julia|go|rust|ruby|php|swift|kotlin)\b'
        for match in re.finditer(prog_lang_pattern, text_lower):
            lang = match.group(1)
            if lang == 'r':
                # Confirm it's the language R, not just the letter
                if re.search(r'\br\b.*(?:programming|language|studio)', text_lower):
                    extracted_skills.append('R')
            else:
                skill_name = self.skill_lookup.get(lang, lang.title())
                if skill_name not in extracted_skills:
                    extracted_skills.append(skill_name)
        
        # Pattern: AWS/GCP/Azure services
        cloud_pattern = r'\b(aws|gcp|azure|s3|ec2|lambda|sagemaker|bigquery|redshift)\b'
        for match in re.finditer(cloud_pattern, text_lower):
            service = self.skill_lookup.get(match.group(1), match.group(1).upper())
            if service not in extracted_skills:
                extracted_skills.append(service)
        
        return extracted_skills
    
    def _spacy_extraction(self, text: str) -> List[str]:
        """Extract skills using spaCy NER and pattern matching."""
        if not self.nlp:
            return []
        
        extracted_skills = []
        doc = self.nlp(text)
        
        # Check noun chunks and entities for skill matches
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            if chunk_text in self.skill_lookup:
                extracted_skills.append(self.skill_lookup[chunk_text])
        
        # Check individual tokens
        for token in doc:
            if not token.is_stop and not token.is_punct:
                token_text = token.text.lower()
                if token_text in self.skill_lookup:
                    extracted_skills.append(self.skill_lookup[token_text])
        
        return extracted_skills
    
    def extract_skills_from_jobs(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract skills from job descriptions in a DataFrame.
        
        Args:
            jobs_df: DataFrame with job descriptions
            
        Returns:
            DataFrame with added 'skills' column
        """
        logger.info(f"Extracting skills from {len(jobs_df)} job postings")
        
        jobs_df = jobs_df.copy()
        jobs_df['skills'] = jobs_df['description'].apply(
            lambda x: self.extract_skills(str(x), method="hybrid")
        )
        jobs_df['skill_count'] = jobs_df['skills'].apply(len)
        
        logger.info(f"Extraction complete. Average skills per job: {jobs_df['skill_count'].mean():.1f}")
        
        return jobs_df
    
    def compute_skill_demand(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute skill demand statistics from job postings.
        Handles both LDJSON format (list of skills) and CSV format (string).
        
        Args:
            jobs_df: DataFrame with 'skills' column
            
        Returns:
            DataFrame with skill demand metrics
        """
        if 'skills' not in jobs_df.columns:
            logger.error("No 'skills' column found in jobs DataFrame")
            return pd.DataFrame()
        
        # Flatten all skills
        all_skills = []
        for skills_data in jobs_df['skills']:
            # Skip if None or empty
            if skills_data is None or (isinstance(skills_data, float) and pd.isna(skills_data)):
                continue
            
            # Handle different formats
            if isinstance(skills_data, list):
                # LDJSON format - already a list
                all_skills.extend(skills_data)
            elif isinstance(skills_data, str):
                # CSV format - might be string representation of list or comma-separated
                try:
                    # Try parsing as list literal
                    import ast
                    parsed = ast.literal_eval(skills_data)
                    if isinstance(parsed, list):
                        all_skills.extend(parsed)
                    else:
                        all_skills.append(str(parsed))
                except (ValueError, SyntaxError):
                    # Fallback to comma-separated
                    skills_list = [s.strip() for s in skills_data.split(',') if s.strip()]
                    all_skills.extend(skills_list)
        
        if not all_skills:
            logger.warning("No skills found in jobs data")
            return pd.DataFrame()
        
        # Count occurrences
        skill_counts = pd.Series(all_skills).value_counts()
        
        # Create demand DataFrame
        total_jobs = len(jobs_df)
        demand_df = pd.DataFrame({
            'skill': skill_counts.index,
            'job_count': skill_counts.values,
            'percentage': (skill_counts.values / total_jobs * 100).round(2)
        })
        
        # Add category information
        demand_df['category'] = demand_df['skill'].apply(self._get_skill_category)
        
        demand_df = demand_df.sort_values('job_count', ascending=False).reset_index(drop=True)
        
        logger.info(f"Computed demand for {len(demand_df)} unique skills from {total_jobs} jobs")
        
        return demand_df
    
    def _get_skill_category(self, skill: str) -> str:
        """Determine which category a skill belongs to."""
        for category, skills in self.skills_by_category.items():
            if skill in skills:
                return category
        return "other"
    
    def extract_from_resume(self, resume_text: str) -> Dict[str, any]:
        """
        Extract skills from a resume.
        
        Args:
            resume_text: Resume text content
            
        Returns:
            Dictionary with extracted skills and metadata
        """
        skills = self.extract_skills(resume_text, method="hybrid")
        
        return {
            'skills': skills,
            'skill_count': len(skills),
            'skills_by_category': self._group_by_category(skills)
        }
    
    def _group_by_category(self, skills: List[str]) -> Dict[str, List[str]]:
        """Group skills by their categories."""
        grouped = {}
        for skill in skills:
            category = self._get_skill_category(skill)
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(skill)
        return grouped
    
    def compare_skills(self, student_skills: List[str], market_demand: pd.DataFrame, 
                       top_n: int = 50) -> pd.DataFrame:
        """
        Compare student skills against market demand.
        
        Args:
            student_skills: List of skills from student resume
            market_demand: DataFrame with skill demand statistics
            top_n: Number of top market skills to compare
            
        Returns:
            DataFrame with gap analysis
        """
        # Get top market skills
        top_market_skills = market_demand.head(top_n).copy()
        
        # Add student status
        top_market_skills['student_has'] = top_market_skills['skill'].isin(student_skills)
        top_market_skills['gap'] = ~top_market_skills['student_has']
        
        # Categorize demand level
        def categorize_demand(pct):
            if pct >= 30:
                return "High"
            elif pct >= 10:
                return "Medium"
            else:
                return "Low"
        
        top_market_skills['demand_level'] = top_market_skills['percentage'].apply(categorize_demand)
        
        return top_market_skills


def main():
    """Demo execution."""
    extractor = SkillExtractor()
    
    # Sample job description
    sample_job = """
    We are seeking a Senior Data Scientist to join our team.
    
    Required Skills:
    - Python and SQL
    - Machine learning with scikit-learn, TensorFlow, and PyTorch
    - Experience with AWS (S3, EC2, SageMaker)
    - PySpark for big data processing
    - Data visualization with Tableau or PowerBI
    - Strong communication skills
    
    Preferred:
    - Docker and Kubernetes
    - MLOps experience
    - Apache Airflow
    """
    
    skills = extractor.extract_skills(sample_job)
    print(f"\nExtracted {len(skills)} skills:")
    print(skills)


if __name__ == "__main__":
    main()
