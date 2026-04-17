# Quick Start Guide

## 🚀 Running the Project

### Option 1: Complete Pipeline Script (Recommended for First Run)
```bash
python scripts/run_pipeline.py
```
This runs the entire pipeline and shows results in the terminal.

### Option 2: Step-by-Step Execution

#### Step 1: Collect Job Data
```bash
python scraping/scraper.py
```
Output: `data/raw/jobs.csv` (200 sample jobs)

#### Step 2: Extract Skills and Compute Demand
```bash
python -c "
import pandas as pd
from nlp.skill_extractor import SkillExtractor

jobs_df = pd.read_csv('data/raw/jobs.csv')
extractor = SkillExtractor()
jobs_with_skills = extractor.extract_skills_from_jobs(jobs_df)
demand_df = extractor.compute_skill_demand(jobs_with_skills)

jobs_with_skills.to_csv('data/processed/jobs_with_skills.csv', index=False)
demand_df.to_csv('data/processed/skill_demand.csv', index=False)

print(f'✓ Processed {len(jobs_df)} jobs')
print(f'✓ Found {len(demand_df)} unique skills')
"
```

#### Step 3: Launch Dashboard
```bash
streamlit run frontend/app.py
```
Access at: http://localhost:8501

#### Step 4: (Optional) Launch API
```bash
python backend/main.py
```
API at: http://localhost:8000  
Docs at: http://localhost:8000/docs

#### Step 5: (Optional) Run PySpark Analytics
```bash
python spark_jobs/skill_demand_analyzer.py
```

## 📊 Using the Dashboard

1. **Market Overview**: View top skills, demand statistics, and market trends
2. **Skill Gap Analysis**: Upload your resume and see skill gaps
3. **Data Explorer**: Browse and filter all skills and jobs

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_nlp.py -v

# Integration tests
pytest tests/test_integration.py -v -m integration
```

## 📁 Key Files

- `scraping/scraper.py` - Job collection
- `nlp/skill_extractor.py` - NLP extraction
- `nlp/skill_dictionary.json` - 200+ skills
- `spark_jobs/skill_demand_analyzer.py` - PySpark analytics
- `backend/main.py` - FastAPI service
- `frontend/app.py` - Streamlit dashboard
- `data/raw/` - Raw job data
- `data/processed/` - Processed results

## 🔧 Configuration

Edit `.env` (copy from `.env.example`) for:
- Supabase credentials (optional)
- API settings
- Spark configuration

## 💡 Common Tasks

### Analyze Your Resume
```python
from nlp.skill_extractor import SkillExtractor
import pandas as pd

extractor = SkillExtractor()

# Load your resume
with open('my_resume.txt', 'r') as f:
    resume_text = f.read()

# Extract skills
resume_skills = extractor.extract_from_resume(resume_text)

# Load market demand
demand_df = pd.read_csv('data/processed/skill_demand.csv')

# Compare
gap_df = extractor.compare_skills(
    student_skills=resume_skills['skills'],
    market_demand=demand_df,
    top_n=50
)

print(gap_df)
```

### Get Top Skills
```python
import pandas as pd

demand_df = pd.read_csv('data/processed/skill_demand.csv')
top_20 = demand_df.head(20)
print(top_20)
```

## 🆘 Troubleshooting

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### No data available in dashboard
```bash
# Run pipeline first
python scripts/run_pipeline.py
```

### Import errors
```bash
# Install from project root
pip install -e .
```

## 📚 Documentation

- Full README: `README.md`
- Architecture: `docs/ARCHITECTURE.md`
- API docs: http://localhost:8000/docs (when API is running)

## 🎯 Example Workflow

1. Install dependencies: `pip install -r requirements.txt`
2. Download spaCy model: `python -m spacy download en_core_web_sm`
3. Run pipeline: `python scripts/run_pipeline.py`
4. Launch dashboard: `streamlit run frontend/app.py`
5. Upload your resume and analyze skill gaps!
