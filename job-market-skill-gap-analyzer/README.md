# Job Market Skill Gap Analyzer

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red.svg)](https://streamlit.io/)
[![PySpark](https://img.shields.io/badge/PySpark-3.5-orange.svg)](https://spark.apache.org/)

An AI-powered system that analyzes job market data to identify in-demand skills and computes personalized skill gap analysis for data science and data engineering professionals.

## 📋 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [API Documentation](#api-documentation)
- [Future Improvements](#future-improvements)

## 🎯 Overview

The Job Market Skill Gap Analyzer is a comprehensive data engineering and machine learning system designed to help students and professionals understand current job market demands and identify skill gaps in their profiles.

The system:
1. **Collects** job postings for Data Scientist/Engineer roles
2. **Extracts** required skills using advanced NLP techniques
3. **Analyzes** skill demand at scale using PySpark
4. **Compares** market demand against individual skill profiles
5. **Visualizes** results through an interactive Streamlit dashboard

## 🔍 Problem Statement

In today's rapidly evolving tech landscape, professionals face several challenges:

- **Information Overload**: Hundreds of job postings with varying requirements
- **Skill Uncertainty**: Unclear which skills are most valuable in the market
- **Gap Identification**: Difficulty understanding personal skill deficiencies
- **Career Planning**: Limited data-driven guidance for skill development

This project solves these problems by providing:
- **Data-driven insights** into skill demand across the job market
- **Automated skill extraction** from resumes and job descriptions
- **Personalized gap analysis** with actionable recommendations
- **Visual analytics** for easy interpretation

## ✨ Key Features

### Data Collection
- Web scraping framework for job postings
- Fallback to realistic sample data generation
- Support for multiple job sources

### NLP Skill Extraction
- Hybrid approach combining spaCy, regex, and dictionary matching
- Curated skill dictionary with 200+ technical skills
- Categorized skills (ML, Big Data, Cloud, etc.)
- High accuracy skill identification

### Big Data Analytics
- PySpark-based distributed processing
- Skill demand computation and aggregation
- Co-occurrence pattern analysis
- Category-level statistics

### Backend API
- RESTful API built with FastAPI
- Resume upload and analysis endpoints
- Real-time skill demand queries
- Database integration with Supabase

### Frontend Dashboard
- Interactive Streamlit interface
- Visual skill gap analysis
- Market overview with charts
- Downloadable reports

### Database
- PostgreSQL/Supabase integration
- Efficient schema design
- Automatic data synchronization
- File-based fallback storage

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Collection Layer                     │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │ Job Scraper  │───▶│  Raw Jobs    │───▶│ Sample Generator│  │
│  └──────────────┘    └──────────────┘    └─────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                      NLP Processing Layer                        │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │ spaCy Model  │───▶│Skill Extract │◀───│ Skill Dictionary│  │
│  └──────────────┘    └──────────────┘    └─────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                     Big Data Analytics Layer                     │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │   PySpark    │───▶│Skill Demand  │───▶│ Aggregations    │  │
│  └──────────────┘    └──────────────┘    └─────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                     Storage & API Layer                          │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │  PostgreSQL  │◀───│   FastAPI    │───▶│   File Storage  │  │
│  │  (Supabase)  │    └──────────────┘    └─────────────────┘  │
│  └──────────────┘            │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                     Presentation Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Streamlit Dashboard                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   Market     │  │  Skill Gap   │  │     Data     │  │  │
│  │  │   Overview   │  │   Analysis   │  │   Explorer   │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Core Technologies
- **Language**: Python 3.9+
- **Framework**: FastAPI, Streamlit
- **NLP**: spaCy, regex
- **Big Data**: Apache Spark (PySpark)
- **Database**: PostgreSQL (Supabase)
- **Visualization**: Plotly

### Key Libraries
- **Data Processing**: pandas, numpy
- **Web Scraping**: requests, BeautifulSoup
- **API**: FastAPI, uvicorn, pydantic
- **Database**: sqlalchemy, psycopg2, supabase-py
- **Testing**: pytest, httpx

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- (Optional) Supabase account for database features

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/job-market-skill-gap-analyzer.git
cd job-market-skill-gap-analyzer
├── notebooks/        # Jupyter notebooks for exploration
└── scripts/          # Utility scripts
```

## Getting Started

### Prerequisites
- Python 3.8+
- Apache Spark 3.x
- Node.js (for frontend)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/job-market-skill-gap-analyzer.git
cd job-market-skill-gap-analyzer
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Download spaCy model
```bash
python -m spacy download en_core_web_sm
```

5. Set up environment variables (optional)
```bash
cp .env.example .env
# Edit .env with your Supabase credentials if using database
```

## 🚀 Usage

### Quick Start - Complete Pipeline

#### 1. Collect Job Data
```bash
python scraping/scraper.py
```
Generates 200 sample job postings in `data/raw/jobs.csv`

#### 2. Extract Skills with NLP
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

print(f'Extracted {len(demand_df)} unique skills from {len(jobs_df)} jobs')
"
```

#### 3. Launch Streamlit Dashboard
```bash
streamlit run frontend/app.py
```
Access at `http://localhost:8501`

#### 4. (Optional) Launch API Server
```bash
python backend/main.py
```
API: `http://localhost:8000` | Docs: `http://localhost:8000/docs`

## 📁 Project Structure

Complete structure with all modules: scraping, NLP, Spark, backend, frontend, data directories, tests, and documentation.

## 🔧 How It Works

### NLP Skill Extraction
Hybrid approach using spaCy, regex, and dictionary matching with 200+ technical skills across categories.

### Skill Demand Computation
```python
demand_percentage = (jobs_with_skill / total_jobs) * 100
High: >=30% | Medium: 10-29% | Low: <10%
```

### Skill Gap Analysis
Compares student skills against top market demand with clear present/missing indicators.

## 📊 API Documentation

RESTful API with endpoints for health check, skill demand, resume analysis, file upload, and job statistics.

Full docs at `http://localhost:8000/docs`

## 🔮 Future Improvements

- Real-time scraping with official APIs
- Transformer models for NLP
- Skill trend analysis
- Salary prediction
- Learning path recommendations
- Docker deployment

## 📄 License

MIT License

## 👥 Authors

Data Engineering Team

---

**Built with ❤️ for the data science community**
