from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="job-market-skill-gap-analyzer",
    version="1.0.0",
    author="Data Engineering Team",
    description="AI-powered job market analysis and skill gap identification system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/job-market-skill-gap-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "job-analyzer-api=backend.main:main",
            "job-analyzer-scrape=scraping.scraper:main",
            "job-analyzer-spark=spark_jobs.skill_demand_analyzer:main",
        ],
    },
)
