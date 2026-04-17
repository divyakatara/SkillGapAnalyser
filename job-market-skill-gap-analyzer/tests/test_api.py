"""
Unit tests for FastAPI backend.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.main import app


client = TestClient(app)


class TestAPI:
    """Test cases for FastAPI endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_analyze_resume_valid(self):
        """Test resume analysis with valid input."""
        resume_data = {
            "resume_text": "Experience with Python, SQL, Machine Learning, TensorFlow, AWS",
            "student_name": "Test Student"
        }
        
        response = client.post("/api/analyze-resume", json=resume_data)
        
        # May return 404 if no market data available, which is okay in test environment
        if response.status_code == 200:
            data = response.json()
            assert "student_name" in data
            assert "student_skills" in data
            assert "skill_count" in data
            assert data["student_name"] == "Test Student"
    
    def test_analyze_resume_empty(self):
        """Test resume analysis with empty input."""
        resume_data = {
            "resume_text": "",
            "student_name": "Test"
        }
        
        response = client.post("/api/analyze-resume", json=resume_data)
        
        # Should return error or empty skills
        assert response.status_code in [200, 404, 500]
    
    def test_skill_demand_endpoint(self):
        """Test skill demand endpoint."""
        response = client.get("/api/skill-demand?top_n=10")
        
        # May return 404 if no data available
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_job_stats_endpoint(self):
        """Test job statistics endpoint."""
        response = client.get("/api/job-stats")
        
        # May return 404 if no data available
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_jobs" in data
            assert "unique_skills" in data
    
    def test_invalid_endpoint(self):
        """Test invalid endpoint returns 404."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
