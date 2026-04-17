🚀 Skill Gap Analyser

AI-Powered Job Market & Skill Gap Analysis System

📌 Overview

The Skill Gap Analyser is an intelligent system that analyzes job market trends and compares them with a user’s existing skill set to identify missing or in-demand skills.

It leverages Natural Language Processing (NLP), data scraping, and analytics to help users understand:

What skills are currently in demand
Where they stand in comparison
What they should learn next
🎯 Key Features
🔍 Skill Extraction
Extracts skills from job descriptions using NLP
Uses a custom-built skill dictionary
📊 Skill Gap Analysis
Compares user skills with market demand
Identifies missing and overlapping skills
📈 Demand Analysis
Analyzes trends across multiple job listings
Highlights high-demand technologies
🌐 Job Data Scraping
Scrapes real-time job listings
Processes and structures raw job data
⚙️ Scalable Data Processing
Uses distributed processing (Spark jobs) for large datasets
🧪 Testing Suite
Includes unit and integration tests for reliability
🧠 Tech Stack

Frontend

Next.js
Tailwind CSS

Backend

Python
Flask

Data & Processing

Apache Spark
NLP techniques for text processing

Other Tools

Git
GitHub
🗂️ Project Structure
job-market-skill-gap-analyzer/
│
├── frontend-nextjs/       # Frontend application (Next.js + Tailwind)
├── nlp/                   # Skill extraction & NLP logic
├── scraping/              # Job scraping modules
├── spark_jobs/            # Demand analysis using Spark
├── tests/                 # Unit & integration tests
├── notebooks/             # Exploratory analysis
├── scripts/               # Pipeline execution scripts
├── app.py                 # Backend entry point
├── requirements.txt       # Dependencies
└── setup.py               # Project setup
⚙️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/divyakatara/SkillGapAnalyser.git
cd SkillGapAnalyser
2️⃣ Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
3️⃣ Install dependencies
pip install -r requirements.txt
4️⃣ Run the application
python app.py
🔄 Workflow
Scrape job data
Process and clean data
Extract skills using NLP
Analyze demand trends
Compare with user skills
Generate insights
📊 Example Use Case
Input: User skills (e.g., Python, SQL)
System Output:
Missing skills (e.g., Docker, AWS)
High-demand skills in market
Recommendations for improvement
🧪 Running Tests
pytest tests/
🚀 Future Enhancements
Personalized learning recommendations
Resume parsing integration
Real-time dashboard with visual analytics
AI-based career path prediction
Integration with LinkedIn/job APIs
📌 Applications
Students planning careers
Job seekers upskilling
Career counselors
EdTech platforms
🤝 Contributing

Contributions are welcome!
Feel free to fork the repo and submit a pull request.

📄 License

This project is for academic and research purposes.

👩‍💻 Author

Divya Katara

⭐ If you like this project

Give it a star on GitHub — it helps a lot!
