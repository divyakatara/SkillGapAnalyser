-- Database schema for Job Market Skill Gap Analyzer
-- PostgreSQL / Supabase

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(200),
    location VARCHAR(200),
    description TEXT,
    date_posted VARCHAR(20),
    salary_min INTEGER,
    salary_max INTEGER,
    source VARCHAR(50),
    skills JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on job_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);

-- Skill demand table
CREATE TABLE IF NOT EXISTS skill_demand (
    id SERIAL PRIMARY KEY,
    skill VARCHAR(100) UNIQUE NOT NULL,
    job_count INTEGER NOT NULL,
    percentage FLOAT NOT NULL,
    demand_level VARCHAR(20),
    category VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on skill for faster lookups
CREATE INDEX IF NOT EXISTS idx_skill_demand_skill ON skill_demand(skill);
CREATE INDEX IF NOT EXISTS idx_skill_demand_level ON skill_demand(demand_level);
CREATE INDEX IF NOT EXISTS idx_skill_demand_category ON skill_demand(category);

-- Student analysis table
CREATE TABLE IF NOT EXISTS student_analysis (
    id SERIAL PRIMARY KEY,
    student_name VARCHAR(200),
    resume_text TEXT,
    skills JSONB,
    skill_count INTEGER,
    gap_analysis JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on student_name
CREATE INDEX IF NOT EXISTS idx_student_analysis_name ON student_analysis(student_name);
CREATE INDEX IF NOT EXISTS idx_student_analysis_created ON student_analysis(created_at DESC);

-- Skill co-occurrence table (optional - for advanced analytics)
CREATE TABLE IF NOT EXISTS skill_cooccurrence (
    id SERIAL PRIMARY KEY,
    skill1 VARCHAR(100) NOT NULL,
    skill2 VARCHAR(100) NOT NULL,
    cooccurrence_count INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(skill1, skill2)
);

CREATE INDEX IF NOT EXISTS idx_cooccurrence_skills ON skill_cooccurrence(skill1, skill2);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skill_demand_updated_at BEFORE UPDATE ON skill_demand
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cooccurrence_updated_at BEFORE UPDATE ON skill_cooccurrence
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
