"""
Unit tests for NLP skill extraction module.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nlp.skill_extractor import SkillExtractor


class TestSkillExtractor:
    """Test cases for SkillExtractor class."""
    
    @pytest.fixture
    def extractor(self):
        """Create a skill extractor instance."""
        return SkillExtractor()
    
    def test_extractor_initialization(self, extractor):
        """Test extractor initializes correctly."""
        assert extractor is not None
        assert len(extractor.all_skills) > 0
        assert len(extractor.skills_by_category) > 0
    
    def test_skill_dictionary_loaded(self, extractor):
        """Test skill dictionary is loaded."""
        assert 'Python' in extractor.all_skills
        assert 'SQL' in extractor.all_skills
        assert 'Machine Learning' in extractor.all_skills
    
    def test_extract_skills_regex(self, extractor):
        """Test regex-based skill extraction."""
        text = """
        We are looking for a Data Scientist with experience in:
        - Python and SQL
        - Machine Learning with TensorFlow
        - AWS cloud platform
        - Data visualization with Tableau
        """
        
        skills = extractor.extract_skills(text, method="regex")
        
        assert 'Python' in skills
        assert 'SQL' in skills
        assert 'Machine Learning' in skills or 'TensorFlow' in skills
        assert 'AWS' in skills or 'Tableau' in skills
    
    def test_extract_skills_hybrid(self, extractor):
        """Test hybrid skill extraction."""
        text = "Experience with Python, pandas, scikit-learn, AWS S3, and PostgreSQL required."
        
        skills = extractor.extract_skills(text, method="hybrid")
        
        assert len(skills) > 0
        assert any(s in skills for s in ['Python', 'Pandas', 'AWS', 'PostgreSQL'])
    
    def test_extract_from_resume(self, extractor):
        """Test resume skill extraction."""
        resume_text = """
        John Doe
        Data Scientist
        
        Skills:
        - Python, SQL, R
        - Machine Learning: scikit-learn, TensorFlow, PyTorch
        - Big Data: Apache Spark, Hadoop
        - Cloud: AWS (S3, EC2, SageMaker)
        - Visualization: Tableau, PowerBI
        """
        
        result = extractor.extract_from_resume(resume_text)
        
        assert 'skills' in result
        assert 'skill_count' in result
        assert result['skill_count'] > 0
        assert 'Python' in result['skills']
    
    def test_compute_skill_demand(self, extractor):
        """Test skill demand computation."""
        jobs_df = pd.DataFrame({
            'description': [
                'Python and SQL required',
                'Python and AWS experience',
                'SQL and Tableau skills'
            ],
            'skills': [
                ['Python', 'SQL'],
                ['Python', 'AWS'],
                ['SQL', 'Tableau']
            ]
        })
        
        demand_df = extractor.compute_skill_demand(jobs_df)
        
        assert len(demand_df) > 0
        assert 'skill' in demand_df.columns
        assert 'percentage' in demand_df.columns
        
        # Python should have highest demand (2/3 = 66.67%)
        python_row = demand_df[demand_df['skill'] == 'Python']
        if not python_row.empty:
            assert python_row.iloc[0]['percentage'] > 60
    
    def test_compare_skills(self, extractor):
        """Test skill gap analysis."""
        student_skills = ['Python', 'SQL']
        
        market_demand = pd.DataFrame({
            'skill': ['Python', 'SQL', 'AWS', 'Docker'],
            'job_count': [90, 80, 70, 60],
            'percentage': [90.0, 80.0, 70.0, 60.0],
            'demand_level': ['High', 'High', 'High', 'High'],
            'category': ['programming_languages'] * 4
        })
        
        gap_df = extractor.compare_skills(student_skills, market_demand, top_n=4)
        
        assert len(gap_df) == 4
        assert 'student_has' in gap_df.columns
        assert 'gap' in gap_df.columns
        
        # Check Python is marked as present
        python_row = gap_df[gap_df['skill'] == 'Python']
        assert python_row.iloc[0]['student_has'] == True
        assert python_row.iloc[0]['gap'] == False
        
        # Check AWS is marked as gap
        aws_row = gap_df[gap_df['skill'] == 'AWS']
        assert aws_row.iloc[0]['student_has'] == False
        assert aws_row.iloc[0]['gap'] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
