"""
Streamlit frontend dashboard for Job Market Skill Gap Analyzer.
A modern, professional dashboard for analyzing job market trends and identifying skill gaps.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from typing import Dict, List
import logging
import pdfplumber
import io
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nlp.skill_extractor import SkillExtractor
from backend.database import FileStorage

# Page configuration
st.set_page_config(
    page_title="SkillScope | Job Market Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, clean design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    .main {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 3rem 2rem 2rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 300;
        opacity: 0.95;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 2rem;
        font-weight: 600;
        color: #2d3748;
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Card Styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin: 1rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.12);
    }
    
    /* Status Badges */
    .skill-badge-present {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #0d4f2e;
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.3rem;
    }
    
    .skill-badge-missing {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #8b2500;
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.3rem;
    }
    
    /* Info Boxes */
    .info-box {
        background: white;
        border-left: 5px solid #667eea;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Spacing & Layout */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #718096;
        font-size: 0.9rem;
        margin-top: 3rem;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize services
def extract_text_from_pdf(pdf_file) -> tuple[str, str]:
    """
    Extract and clean text from uploaded PDF file.
    
    Args:
        pdf_file: Streamlit UploadedFile object containing PDF data
        
    Returns:
        tuple: (extracted_text, status_message)
    """
    try:
        # Read PDF bytes into memory
        pdf_bytes = pdf_file.read()
        
        # Open PDF with pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # Extract text from all pages
            text_parts = []
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            if not text_parts:
                return "", "❌ Could not extract text from PDF. The file may contain only images or be encrypted."
            
            # Combine all pages
            full_text = "\n\n".join(text_parts)
            
            # Clean the text
            # Remove excessive whitespace
            full_text = re.sub(r'\s+', ' ', full_text)
            # Remove common header/footer patterns (page numbers, etc.)
            full_text = re.sub(r'\b(Page|page)\s*\d+\s*(of|\/)\s*\d+\b', '', full_text)
            # Normalize line breaks
            full_text = full_text.strip()
            
            if len(full_text) < 50:
                return "", "⚠️ PDF contains very little text. Please ensure it's a text-based PDF, not a scanned image."
            
            page_count = len(pdf.pages)
            char_count = len(full_text)
            
            return full_text, f"✅ Successfully extracted {char_count:,} characters from {page_count} page(s)"
            
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return "", f"❌ Error reading PDF: {str(e)}"


@st.cache_resource
def get_skill_extractor():
    """Initialize skill extractor (cached)."""
    return SkillExtractor()


@st.cache_resource
def get_storage():
    """Initialize storage (cached)."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    return FileStorage(str(data_dir))


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def load_market_data():
    """
    STAGE 1 & 2: Load skill demand data from cache.
    If cache missing, triggers expensive NLP processing (2-5 minutes).
    This function runs ONCE per session due to caching.
    """
    storage = get_storage()
    
    # STAGE 1: Try to load from cache (fast - takes ~1 second)
    demand_df = storage.load_skill_demand()
    
    if not demand_df.empty:
        # Cache hit - instant load
        logger.info(f"✓ Loaded {len(demand_df)} skills from cache (fast path)")
        
        # Add demand_level if missing
        if 'demand_level' not in demand_df.columns:
            demand_df['demand_level'] = pd.cut(
                demand_df['percentage'],
                bins=[0, 20, 50, 100],
                labels=['Low', 'Medium', 'High']
            )
        
        return demand_df
    
    # STAGE 2: No cache - must process from source (slow - 2-5 minutes)
    # This only happens once, then cache is used
    st.warning("⚠️ First-time data processing required. This will take 2-5 minutes...")
    
    progress_bar = st.progress(0, text="Loading raw job data...")
    
    try:
        # Step 1: Load jobs (10%)
        jobs_df = storage.load_jobs()
        
        if jobs_df.empty:
            st.error("❌ Failed to load jobs from data file")
            return pd.DataFrame()
        
        progress_bar.progress(10, text=f"Loaded {len(jobs_df):,} jobs. Initializing NLP engine...")
        
        # Step 2: Initialize extractor (20%)
        extractor = get_skill_extractor()
        progress_bar.progress(20, text="Extracting skills from job descriptions...")
        
        # Step 3: Extract skills (80% - this is the slow part)
        jobs_with_skills = extractor.extract_skills_from_jobs(jobs_df)
        
        if jobs_with_skills.empty or 'skills' not in jobs_with_skills.columns:
            st.error("❌ Failed to extract skills")
            return pd.DataFrame()
        
        progress_bar.progress(80, text="Computing skill demand metrics...")
        
        # Step 4: Compute demand (90%)
        demand_df = extractor.compute_skill_demand(jobs_with_skills)
        
        if demand_df.empty:
            st.error("❌ Failed to compute skill demand")
            return pd.DataFrame()
        
        progress_bar.progress(95, text="Saving cache for future use...")
        
        # Step 5: Cache results (100%)
        storage.save_jobs(jobs_with_skills)
        storage.save_skill_demand(demand_df)
        
        progress_bar.progress(100, text="✓ Processing complete!")
        progress_bar.empty()  # Remove progress bar
        
        st.success(f"✓ Successfully processed {len(demand_df)} skills. Future loads will be instant!")
        
        # Add demand_level
        if 'demand_level' not in demand_df.columns:
            demand_df['demand_level'] = pd.cut(
                demand_df['percentage'],
                bins=[0, 20, 50, 100],
                labels=['Low', 'Medium', 'High']
            )
        
        return demand_df
        
    except Exception as e:
        st.error(f"❌ Error during processing: {e}")
        logger.error(f"Error in load_market_data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def load_job_data():
    """
    STAGE 1: Load job postings data from cache (fast).
    Uses processed jobs with skills if available, raw data otherwise.
    """
    storage = get_storage()
    
    # Try to load cached jobs with extracted skills first (preferred)
    jobs_df = storage.load_jobs_with_skills()
    
    if not jobs_df.empty:
        logger.info(f"✓ Loaded {len(jobs_df)} jobs with skills from cache (fast path)")
        return jobs_df
    
    # Fallback: load raw jobs from XLS
    logger.info("Loading raw jobs from India_tech_jobs.xls...")
    jobs_df = storage.load_jobs()
    
    if not jobs_df.empty:
        logger.info(f"Loaded {len(jobs_df)} jobs from XLS source")
    else:
        logger.warning("No job data available from XLS")
    
    return jobs_df


def create_demand_chart(demand_df: pd.DataFrame, top_n: int = 20):
    """Create modern skill demand visualization."""
    top_skills = demand_df.head(top_n)
    
    fig = px.bar(
        top_skills,
        x='percentage',
        y='skill',
        orientation='h',
        title=f'Most Sought-After Skills in the Market',
        labels={'percentage': 'Presence in Job Postings (%)', 'skill': ''},
        color='category',
        color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b']
    )
    
    fig.update_layout(
        height=600,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=True,
        title_font_size=20,
        title_font_family='Inter',
        font=dict(family='Inter', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    fig.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(gridcolor='rgba(0,0,0,0)')
    
    return fig


def generate_skill_explanation(skill: str, percentage: float, category: str, demand_level: str) -> str:
    """
    Generate a contextual explanation for why a skill matters in the job market.
    Based on actual data: frequency, category, and demand level.
    
    Args:
        skill: The skill name
        percentage: Percentage of jobs requiring this skill
        category: Skill category (e.g., 'programming', 'cloud', 'databases')
        demand_level: 'High', 'Medium', or 'Low'
        
    Returns:
        A concise 1-2 line explanation
    """
    # Role mapping based on skill categories and common patterns
    skill_lower = skill.lower()
    category_lower = category.lower() if category else ""
    
    # Determine relevant roles
    if any(term in skill_lower for term in ['python', 'java', 'javascript', 'react', 'node', 'angular']):
        roles = "Software Engineers, Full-Stack Developers"
    elif any(term in skill_lower for term in ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'ai']):
        roles = "Data Scientists, ML Engineers, AI Specialists"
    elif any(term in skill_lower for term in ['sql', 'database', 'postgresql', 'mongodb', 'mysql']):
        roles = "Database Administrators, Backend Developers, Data Engineers"
    elif any(term in skill_lower for term in ['aws', 'azure', 'gcp', 'cloud', 'kubernetes', 'docker']):
        roles = "DevOps Engineers, Cloud Architects, Platform Engineers"
    elif any(term in skill_lower for term in ['data', 'analytics', 'tableau', 'powerbi', 'visualization']):
        roles = "Data Analysts, Business Intelligence Developers"
    elif any(term in skill_lower for term in ['ui', 'ux', 'design', 'figma', 'css']):
        roles = "UI/UX Designers, Frontend Developers"
    elif any(term in skill_lower for term in ['security', 'cybersecurity', 'encryption']):
        roles = "Security Engineers, Cybersecurity Analysts"
    elif 'programming' in category_lower or 'development' in category_lower:
        roles = "Software Developers, Engineers"
    else:
        roles = "various tech roles"
    
    # Generate explanation based on demand level and percentage
    if demand_level == 'High':
        if percentage >= 40:
            return f"Critical skill for {roles}. Required by nearly half of all job postings, indicating it's industry-standard."
        elif percentage >= 30:
            return f"Essential for {roles}. Frequently requested across {percentage:.0f}% of positions, highly valued by employers."
        else:
            return f"Important for {roles}. Found in {percentage:.0f}% of jobs, showing strong market demand."
    elif demand_level == 'Medium':
        if percentage >= 20:
            return f"Valuable for {roles}. Present in {percentage:.0f}% of listings, beneficial for career advancement."
        else:
            return f"Useful for {roles}. Appears in {percentage:.0f}% of postings, growing in popularity."
    else:
        return f"Emerging skill for {roles}. Found in {percentage:.0f}% of jobs, good to have for specialization."


def create_gap_analysis_chart(gap_df: pd.DataFrame):
    """Create professional skill gap comparison visualization with clear visual distinction."""
    top_gaps = gap_df.head(30)
    
    fig = go.Figure()
    
    # Separate skills into two groups for visual clarity
    skills_you_have = top_gaps[top_gaps['student_has'] == True]
    skills_missing = top_gaps[top_gaps['student_has'] == False]
    
    # Add bars for skills you're MISSING (red/amber) - higher visual priority
    if not skills_missing.empty:
        # Color code by priority
        colors = skills_missing['demand_level'].map({
            'High': 'rgba(239, 68, 68, 0.7)',      # Red for high priority gaps
            'Medium': 'rgba(251, 146, 60, 0.7)',   # Amber for medium priority
            'Low': 'rgba(156, 163, 175, 0.5)'      # Gray for low priority
        })
        
        fig.add_trace(go.Bar(
            y=skills_missing['skill'],
            x=skills_missing['percentage'],
            name='⚠️ Missing Skills',
            orientation='h',
            marker_color=colors,
            hovertemplate='<b>%{y}</b><br>🎯 Learning Opportunity<br>Demand: %{x:.1f}%<extra></extra>',
            showlegend=True
        ))
    
    # Add bars for skills you HAVE (green) - celebration
    if not skills_you_have.empty:
        fig.add_trace(go.Bar(
            y=skills_you_have['skill'],
            x=skills_you_have['percentage'],
            name='✅ Your Skills',
            orientation='h',
            marker_color='rgba(16, 185, 129, 0.8)',  # Green for matched skills
            hovertemplate='<b>%{y}</b><br>✅ You have this skill<br>Demand: %{x:.1f}%<extra></extra>',
            showlegend=True
        ))
    
    fig.update_layout(
        title='Skills You Have vs. Missing Opportunities',
        xaxis_title='Presence in Job Postings (%)',
        yaxis_title='',
        height=700,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=True,
        title_font_size=20,
        title_font_family='Inter',
        font=dict(family='Inter', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    fig.update_xaxes(gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(gridcolor='rgba(0,0,0,0)')
    
    return fig


def create_category_chart(demand_df: pd.DataFrame):
    """Create skill category distribution visualization."""
    if 'category' not in demand_df.columns:
        return None
    
    category_stats = demand_df.groupby('category').agg({
        'job_count': 'sum',
        'skill': 'count'
    }).reset_index()
    category_stats.columns = ['category', 'total_mentions', 'unique_skills']
    category_stats = category_stats.sort_values('total_mentions', ascending=False)
    
    fig = px.pie(
        category_stats,
        values='total_mentions',
        names='category',
        title='Skills Distribution by Category',
        color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a']
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont_size=12,
        marker=dict(line=dict(color='white', width=2))
    )
    
    fig.update_layout(
        title_font_size=18,
        title_font_family='Inter',
        font=dict(family='Inter', size=11),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def main():
    """Main application entry point."""
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🎯 SkillScope</h1>
        <p class="hero-subtitle">
            Discover market trends, identify skill gaps, and accelerate your career growth 
            with data-driven insights from real job postings
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        page = st.radio(
            "",
            ["Market Insights", "Gap Analysis", "Explore Data"],
            label_visibility="collapsed"
        )
        
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        
        st.markdown("### 💡 About This Tool")
        st.markdown("""
        <div class="info-box">
            <p style="margin: 0; line-height: 1.6;">
                SkillScope analyzes real job market data to help you:
            </p>
            <ul style="margin-top: 0.5rem; line-height: 1.8;">
                <li>Identify trending skills</li>
                <li>Compare your profile with market needs</li>
                <li>Plan your learning roadmap</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # STAGE 3: Load data (uses cache - instant after first load)
    try:
        # Show loading status in sidebar
        with st.sidebar:
            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
            loading_status = st.empty()
            loading_status.info("📊 Loading market data...")
        
        # Load skill demand (cached after first run)
        demand_df = load_market_data()
        
        # Load job data (cached)
        loading_status.info("📋 Loading job postings...")
        jobs_df = load_job_data()
        
        # Clear loading indicator
        loading_status.empty()
        
        if demand_df.empty:
            st.warning("⚠️ No data available yet. Please ensure India_tech_jobs.xls exists in the data/ directory.")
            st.code("Expected file: data/India_tech_jobs.xls", language="text")
            st.info("💡 The XLS file should contain a 'description' column with job posting text.")
            return
        
    except Exception as e:
        st.error(f"❌ Unable to load data: {str(e)}")
        import traceback
        with st.expander("View error details"):
            st.code(traceback.format_exc())
        return
    
    # Route to selected page
    if page == "Market Insights":
        show_market_overview(demand_df, jobs_df)
    elif page == "Gap Analysis":
        show_gap_analysis(demand_df)
    else:
        show_data_explorer(demand_df, jobs_df)
    
    # Footer
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        Built with ❤️ using Streamlit • Data updated dynamically from job market analysis
    </div>
    """, unsafe_allow_html=True)


def show_market_overview(demand_df: pd.DataFrame, jobs_df: pd.DataFrame):
    """Display comprehensive market insights."""
    
    # Section Header
    st.markdown('<h2 class="section-header">📈 Market Insights</h2>', unsafe_allow_html=True)
    st.markdown("Curated analysis of current job market trends and skill demands")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Jobs Analyzed",
            value=f"{len(jobs_df):,}" if not jobs_df.empty else "0",
            help="Total number of job postings analyzed"
        )
    
    with col2:
        st.metric(
            label="Unique Skills Identified",
            value=f"{len(demand_df):,}",
            help="Distinct skills extracted from job postings"
        )
    
    with col3:
        high_demand = len(demand_df[demand_df['percentage'] >= 30])
        st.metric(
            label="High Demand Skills",
            value=high_demand,
            help="Skills appearing in 30%+ of job postings"
        )
    
    with col4:
        if not jobs_df.empty and 'company' in jobs_df.columns:
            companies = jobs_df['company'].nunique()
            st.metric(label="Companies", value=f"{companies:,}")
        else:
            st.metric(label="Categories", value=demand_df['category'].nunique() if 'category' in demand_df.columns else "N/A")
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Dominant Skills in the Market")
        top_n = st.slider("Adjust number of skills displayed:", 10, 50, 20, help="Slide to show more or fewer skills")
        fig = create_demand_chart(demand_df, top_n)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category Distribution
        if 'category' in demand_df.columns:
            st.markdown("### Category Breakdown")
            fig = create_category_chart(demand_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        # Top Skills Summary
        st.markdown("### Most In-Demand")
        top_skills = demand_df.head(10)[['skill', 'percentage']].copy()
        top_skills['percentage'] = top_skills['percentage'].apply(lambda x: f"{x:.1f}%")
        top_skills.columns = ['Skill', 'Demand']
        st.dataframe(top_skills, hide_index=True, use_container_width=True)


def show_gap_analysis(demand_df: pd.DataFrame):
    """Display personalized skill gap analysis."""
    
    st.markdown('<h2 class="section-header">🎯 Gap Analysis</h2>', unsafe_allow_html=True)
    st.markdown("Compare your skills with current market demands and discover growth opportunities")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Input Section
    st.markdown("### 📝 Share Your Profile")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_method = st.radio(
            "How would you like to provide your information?",
            ["Paste Resume or Skills", "Upload Document"],
            horizontal=True
        )
    
    resume_text = ""
    pdf_status_placeholder = st.empty()
    
    if input_method == "Paste Resume or Skills":
        resume_text = st.text_area(
            "Paste your resume, LinkedIn profile, or list of skills:",
            height=250,
            placeholder="Example:\n• Python, JavaScript, React\n• Machine Learning, Data Analysis\n• 5 years experience in web development...",
            help="The more detail you provide, the more accurate your analysis will be"
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or TXT format)",
            type=['pdf', 'txt'],
            help="Upload a PDF or text file containing your resume or skills"
        )
        
        if uploaded_file:
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            if file_type == 'pdf':
                # Extract text from PDF
                with st.spinner("📄 Reading PDF..."):
                    resume_text, status_message = extract_text_from_pdf(uploaded_file)
                    pdf_status_placeholder.info(status_message)
                    
                    # Show preview of extracted text
                    if resume_text:
                        with st.expander("👁️ Preview extracted text"):
                            preview_length = min(500, len(resume_text))
                            st.text(resume_text[:preview_length] + ("..." if len(resume_text) > preview_length else ""))
            
            elif file_type == 'txt':
                # Read text file
                try:
                    resume_text = uploaded_file.read().decode('utf-8')
                    pdf_status_placeholder.success(f"✅ Text file loaded successfully ({len(resume_text):,} characters)")
                except Exception as e:
                    pdf_status_placeholder.error(f"❌ Error reading text file: {str(e)}")
            
            else:
                pdf_status_placeholder.warning("⚠️ Unsupported file format")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔍 Analyze My Skills", type="primary", use_container_width=False):
        if not resume_text:
            st.warning("⚠️ Please provide your resume or skill information above.")
            return
        
        with st.spinner("🔄 Analyzing your profile... This may take a moment."):
            # Extract skills from resume
            extractor = get_skill_extractor()
            resume_data = extractor.extract_from_resume(resume_text)
            student_skills = resume_data['skills']
            
            if not student_skills:
                st.warning("😕 No technical skills detected. Please make sure your text includes relevant skills like programming languages, frameworks, or tools.")
                return
            
            # Compare with market demand
            gap_df = extractor.compare_skills(student_skills, demand_df, top_n=50)
            
            # Calculate Resume Match Score
            matched_count = gap_df['student_has'].sum()
            total_top_skills = len(gap_df)
            match_score = (matched_count / total_top_skills * 100) if total_top_skills > 0 else 0
            
            # Success message
            st.success(f"✅ Successfully identified {len(student_skills)} skills in your profile!")
            
            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
            
            # Resume Match Score - Prominent Display
            st.markdown("### 🎯 Resume Readiness Score")
            
            # Determine score color and status
            if match_score >= 70:
                score_color = "#10b981"  # Green
                score_status = "Excellent"
                score_emoji = "🌟"
                status_bg = "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)"
                status_border = "#10b981"
            elif match_score >= 50:
                score_color = "#3b82f6"  # Blue
                score_status = "Good"
                score_emoji = "👍"
                status_bg = "linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)"
                status_border = "#3b82f6"
            elif match_score >= 30:
                score_color = "#f59e0b"  # Amber
                score_status = "Room for Growth"
                score_emoji = "📈"
                status_bg = "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)"
                status_border = "#f59e0b"
            else:
                score_color = "#ef4444"  # Red
                score_status = "Needs Development"
                score_emoji = "🎯"
                status_bg = "linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)"
                status_border = "#ef4444"
            
            # Display prominent score card
            st.markdown(f"""
            <div style="background: {status_bg}; 
                        padding: 2rem; 
                        border-radius: 12px; 
                        text-align: center; 
                        border: 2px solid {status_border};
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        margin-bottom: 2rem;">
                <h1 style="margin: 0; font-size: 4rem; color: {score_color}; font-weight: bold;">
                    {match_score:.0f}%
                </h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; color: #1f2937;">
                    {score_emoji} {score_status}
                </p>
                <p style="margin: 0.5rem 0 0 0; font-size: 1rem; color: #4b5563;">
                    You match <strong>{matched_count}</strong> out of the top <strong>{total_top_skills}</strong> market-demanded skills
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Summary Metrics
            st.markdown("### 📊 Detailed Breakdown")
            
            col1, col2, col3, col4 = st.columns(4)
            
            missing_count = (~gap_df['student_has']).sum()
            missing_high = gap_df[(gap_df['gap']) & (gap_df['demand_level'] == 'High')].shape[0]
            missing_medium = gap_df[(gap_df['gap']) & (gap_df['demand_level'] == 'Medium')].shape[0]
            
            with col1:
                st.metric("✅ Skills You Have", matched_count)
            
            with col2:
                st.metric("📚 Learning Opportunities", missing_count)
            
            with col3:
                st.metric("🔥 High Priority Gaps", missing_high)
            
            with col4:
                st.metric("⭐ Medium Priority Gaps", missing_medium)
            
            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
            
            # Visualization
            st.markdown("### 📈 Visual Comparison")
            fig = create_gap_analysis_chart(gap_df)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
            
            # Detailed Breakdown
            st.markdown("### 🔍 Detailed Breakdown")
            
            tab1, tab2, tab3 = st.tabs(["🎯 Priority Learning", "✅ Your Strengths", "📋 Complete Analysis"])
            
            with tab1:
                missing_df = gap_df[gap_df['gap'] == True].copy()
                missing_df['priority'] = missing_df['demand_level'].map({
                    'High': 1, 'Medium': 2, 'Low': 3
                })
                missing_df = missing_df.sort_values('priority')
                
                if not missing_df.empty:
                    # Section header with clear visual indicator
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%); 
                                padding: 1rem; border-radius: 8px; margin-bottom: 1rem; 
                                border-left: 4px solid #f59e0b;">
                        <h4 style="margin: 0; color: #92400e;">
                            ⚠️ Skills to Consider Learning
                        </h4>
                        <p style="margin: 0.5rem 0 0 0; color: #78350f; font-size: 0.9rem;">
                            Ranked by market demand - focus on high priority items first
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for idx, row in enumerate(missing_df.head(20).iterrows(), 1):
                        _, row = row
                        if row['demand_level'] == 'High':
                            priority_icon = "🔴"
                            priority_text = "High Priority"
                            card_color = "#fee2e2"
                            border_color = "#dc2626"
                            text_color = "#991b1b"
                        elif row['demand_level'] == 'Medium':
                            priority_icon = "🟡"
                            priority_text = "Medium Priority"
                            card_color = "#fed7aa"
                            border_color = "#ea580c"
                            text_color = "#9a3412"
                        else:
                            priority_icon = "⚪"
                            priority_text = "Consider Learning"
                            card_color = "#f3f4f6"
                            border_color = "#9ca3af"
                            text_color = "#4b5563"
                        
                        # Generate contextual explanation
                        category = row.get('category', '')
                        explanation = generate_skill_explanation(
                            row['skill'], 
                            row['percentage'], 
                            category, 
                            row['demand_level']
                        )
                        
                        st.markdown(f"""
                        <div style="background: {card_color}; padding: 1rem; border-radius: 6px; 
                                    margin-bottom: 0.75rem; border-left: 3px solid {border_color};">
                            <strong style="font-size: 1.1rem; color: #1f2937;">{idx}. {row['skill']}</strong><br>
                            <span style="font-size: 0.95rem; color: {text_color};">
                                {priority_icon} {priority_text} • Found in <strong>{row['percentage']:.1f}%</strong> of job postings
                            </span><br>
                            <span style="font-size: 0.85rem; color: #4b5563; font-style: italic; margin-top: 0.3rem; display: block;">
                                💡 {explanation}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("🎉 Excellent! You have all the highly demanded skills in our dataset!")
            
            with tab2:
                matched_df = gap_df[gap_df['student_has'] == True].sort_values('percentage', ascending=False)
                
                if not matched_df.empty:
                    # Section header with green success theme
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); 
                                padding: 1rem; border-radius: 8px; margin-bottom: 1rem; 
                                border-left: 4px solid #10b981;">
                        <h4 style="margin: 0; color: #065f46;">
                            ✅ Your Skills in Demand
                        </h4>
                        <p style="margin: 0.5rem 0 0 0; color: #047857; font-size: 0.9rem;">
                            These are your marketable strengths - keep them sharp!
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for idx, row in enumerate(matched_df.iterrows(), 1):
                        _, row = row
                        if row['demand_level'] == 'High':
                            demand_badge = "🔥 High Demand"
                            card_color = "#d1fae5"
                            border_color = "#10b981"
                            text_color = "#065f46"
                        elif row['demand_level'] == 'Medium':
                            demand_badge = "⭐ Medium Demand"
                            card_color = "#dbeafe"
                            border_color = "#3b82f6"
                            text_color = "#1e40af"
                        else:
                            demand_badge = "💡 Low Demand"
                            card_color = "#f3f4f6"
                            border_color = "#6b7280"
                            text_color = "#374151"
                        
                        st.markdown(f"""
                        <div style="background: {card_color}; padding: 1rem; border-radius: 6px; 
                                    margin-bottom: 0.75rem; border-left: 3px solid {border_color};">
                            <strong style="font-size: 1.1rem; color: #1f2937;">{idx}. {row['skill']}</strong>
                            <span style="float: right; background: {border_color}; color: white; 
                                        padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem;">
                                ✓ YOU HAVE THIS
                            </span><br>
                            <span style="font-size: 0.95rem; color: {text_color};">
                                {demand_badge} • Found in <strong>{row['percentage']:.1f}%</strong> of jobs
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No matching skills found in our analyzed dataset. Try adding more technical skills to your profile.")
            
            with tab3:
                # Complete comparison table
                display_df = gap_df[['skill', 'percentage', 'demand_level', 'student_has', 'gap']].copy()
                display_df['status'] = display_df['student_has'].map({True: '✅ You Have This', False: '📚 Learn This'})
                display_df = display_df.drop(columns=['student_has', 'gap'])
                display_df.columns = ['Skill', 'Market Demand (%)', 'Priority Level', 'Your Status']
                
                st.dataframe(
                    display_df,
                    hide_index=True,
                    use_container_width=True,
                    height=500
                )


def show_data_explorer(demand_df: pd.DataFrame, jobs_df: pd.DataFrame):
    """Interactive data exploration interface."""
    
    st.markdown('<h2 class="section-header">🔍 Explore Data</h2>', unsafe_allow_html=True)
    st.markdown("Dive deep into the raw data powering this analysis")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Skills Database", "💼 Job Postings"])
    
    with tab1:
        st.markdown("### Skills Intelligence")
        st.markdown("Comprehensive skill demand metrics extracted from job postings")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Filters
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            if 'category' in demand_df.columns:
                categories = ['All Categories'] + sorted(demand_df['category'].unique().tolist())
                selected_category = st.selectbox("📁 Filter by category", categories)
                
                if selected_category != 'All Categories':
                    filtered_df = demand_df[demand_df['category'] == selected_category]
                else:
                    filtered_df = demand_df
            else:
                filtered_df = demand_df
        
        with col2:
            demand_levels = ['All Priority Levels'] + sorted(demand_df['demand_level'].unique().tolist())
            selected_level = st.selectbox("⭐ Filter by priority", demand_levels)
            
            if selected_level != 'All Priority Levels':
                filtered_df = filtered_df[filtered_df['demand_level'] == selected_level]
        
        with col3:
            search_term = st.text_input("🔎 Search skills", placeholder="e.g., Python, React...")
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['skill'].str.contains(search_term, case=False, na=False)
                ]
        
        st.markdown(f"**Showing {len(filtered_df)} of {len(demand_df)} skills**")
        
        # Display data
        display_df = filtered_df.copy()
        if 'category' in display_df.columns:
            display_cols = ['skill', 'percentage', 'job_count', 'demand_level', 'category']
        else:
            display_cols = ['skill', 'percentage', 'job_count', 'demand_level']
        
        display_df = display_df[display_cols]
        display_df.columns = ['Skill', 'Market Demand (%)', 'Appearances', 'Priority', 'Category'] if 'category' in display_df.columns else ['Skill', 'Market Demand (%)', 'Appearances', 'Priority']
        
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            height=500
        )
        
        # Download button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="skillscope_data.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with tab2:
        st.markdown("### Job Postings Archive")
        
        if not jobs_df.empty:
            st.markdown(f"**Total postings in database:** {len(jobs_df):,}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Display relevant columns
            display_cols = [col for col in ['title', 'company', 'location', 'date_posted'] if col in jobs_df.columns]
            
            if display_cols:
                display_df = jobs_df[display_cols].head(100).copy()
                
                # Rename columns for better presentation
                column_mapping = {
                    'title': 'Job Title',
                    'company': 'Company',
                    'location': 'Location',
                    'date_posted': 'Posted Date'
                }
                display_df.columns = [column_mapping.get(col, col) for col in display_df.columns]
                
                st.dataframe(
                    display_df,
                    hide_index=True,
                    use_container_width=True,
                    height=500
                )
                
                st.info(f"📌 Showing first 100 of {len(jobs_df):,} total job postings")
            else:
                st.warning("Job data structure not recognized. Raw data available for download.")
        else:
            st.info("📭 No job posting data available yet. Run the data collection script to populate this section.")


if __name__ == "__main__":
    main()
