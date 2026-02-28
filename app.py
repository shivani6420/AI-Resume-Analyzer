import streamlit as st
import pdfplumber
import re
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
    <style>
        .stApp {
            background-color: #f4f6f9;
            font-family: 'Segoe UI', sans-serif;
        }
        section[data-testid="stSidebar"] {
            background-color: #1a2a4a;
            padding: 20px;
        }
        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] .stTextArea textarea {
            background-color: #243554;
            color: #ffffff !important;
            border: 1px solid #3a5070;
            border-radius: 8px;
        }
        section[data-testid="stSidebar"] .stFileUploader {
            background-color: #243554;
            border-radius: 8px;
            padding: 10px;
        }
        .stButton > button {
            background-color: #0057b8;
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 12px 28px;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            transition: background-color 0.3s;
        }
        .stButton > button:hover {
            background-color: #003d87;
        }
        .card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 5px solid #0057b8;
        }
        .metric-card {
            background-color: #0057b8;
            color: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,87,184,0.3);
        }
        .metric-card h1 {
            font-size: 42px;
            margin: 0;
            color: white;
        }
        .metric-card p {
            font-size: 14px;
            margin: 0;
            opacity: 0.85;
            color: white;
        }
        .badge-green {
            background-color: #e6f4ea;
            color: #1e7e34;
            border-radius: 20px;
            padding: 5px 14px;
            margin: 4px;
            display: inline-block;
            font-size: 13px;
            font-weight: 500;
            border: 1px solid #a8d5b0;
        }
        .badge-red {
            background-color: #fde8e8;
            color: #c0392b;
            border-radius: 20px;
            padding: 5px 14px;
            margin: 4px;
            display: inline-block;
            font-size: 13px;
            font-weight: 500;
            border: 1px solid #f0b0b0;
        }
        .main-header {
            background: linear-gradient(90deg, #0057b8, #003d87);
            color: white;
            padding: 28px 32px;
            border-radius: 12px;
            margin-bottom: 28px;
        }
        .main-header h1 { color: white; margin: 0; font-size: 28px; }
        .main-header p { color: #cce0ff; margin: 6px 0 0 0; font-size: 15px; }
        .section-title {
            font-size: 17px;
            font-weight: 700;
            color: #1a2a4a;
            margin-bottom: 12px;
        }
        .progress-container {
            background-color: #e0e8f0;
            border-radius: 10px;
            height: 22px;
            width: 100%;
            overflow: hidden;
            margin-top: 8px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SKILLS DATABASE
# ─────────────────────────────────────────────
SKILLS_DB = [
    "python", "java", "javascript", "typescript", "c++", "c#", "r", "scala", "go", "kotlin",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle", "nosql",
    "html", "css", "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot",
    "machine learning", "deep learning", "nlp", "computer vision", "data analysis", "data science",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux", "ci/cd", "jenkins",
    "power bi", "tableau", "excel", "hadoop", "spark", "kafka",
    "rest api", "graphql", "microservices", "agile", "scrum"
]

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s\.\+\#]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_skills(text, skills_list):
    found = []
    for skill in skills_list:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            found.append(skill)
    return found

def calculate_match(resume_skills, job_skills):
    if not job_skills:
        return 0, []
    common = set(resume_skills) & set(job_skills)
    missing = set(job_skills) - set(resume_skills)
    match_pct = round((len(common) / len(job_skills)) * 100, 2)
    return match_pct, list(missing)

def generate_suggestion(missing_skills, match_pct):
    if match_pct == 100:
        return "🎉 Perfect match! Your resume aligns completely with the job description."
    elif match_pct >= 75:
        return f"✅ Great profile! Consider strengthening experience in: <b>{', '.join([s.title() for s in missing_skills])}</b>."
    elif match_pct >= 50:
        return f"📈 Decent match. To improve your chances, work on: <b>{', '.join([s.title() for s in missing_skills])}</b>. Add relevant projects or certifications."
    else:
        return f"🚀 Keep building! Focus on learning: <b>{', '.join([s.title() for s in missing_skills])}</b>. Consider online courses or personal projects to close the gap."

def make_gauge(match_pct):
    color = "#27ae60" if match_pct >= 75 else "#f39c12" if match_pct >= 50 else "#e74c3c"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=match_pct,
        number={'suffix': "%", 'font': {'size': 36, 'color': '#1a2a4a'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#aaa"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': '#fde8e8'},
                {'range': [50, 75], 'color': '#fff3cd'},
                {'range': [75, 100], 'color': '#e6f4ea'}
            ],
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.75,
                'value': match_pct
            }
        },
        title={'text': "Match Score", 'font': {'size': 16, 'color': '#1a2a4a'}}
    ))
    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="white",
        font={'color': "#1a2a4a"}
    )
    return fig

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 AI Resume Analyzer")
    st.markdown("---")
    st.markdown("### 📄 Upload Resume")
    uploaded_file = st.file_uploader("PDF format only", type=["pdf"])
    st.markdown("### 📋 Job Description")
    job_desc = st.text_area("Paste the job description here...", height=280)
    st.markdown("---")
    analyze_btn = st.button("🔍 Analyze Resume")

# ─────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────
st.markdown("""
    <div class="main-header">
        <h1>🧠 AI Resume Analyzer</h1>
        <p>Upload your resume and paste a job description to instantly measure your match score and identify skill gaps.</p>
    </div>
""", unsafe_allow_html=True)

# ── DEFAULT / HOW TO USE ──
if not analyze_btn:
    st.markdown("""
        <div class="card" style="text-align:center; padding: 30px 20px;">
            <h2 style="color:#0057b8;">👈 Get Started</h2>
            <p style="color:#555; font-size:16px;">Upload your resume PDF and paste a job description in the sidebar, then click <b>Analyze Resume</b>.</p>
        </div>

        <div class="card" style="border-left-color:#0057b8;">
            <p class="section-title" style="font-size:18px; color:#0057b8;">📖 How to Use</p>
            <table style="width:100%; border-collapse:collapse;">
                <tr style="background-color:#f0f5ff;">
                    <td style="padding:12px; font-size:22px; width:40px;">📄</td>
                    <td style="padding:12px;"><b>Step 1</b> — Upload your resume in PDF format using the sidebar.</td>
                </tr>
                <tr>
                    <td style="padding:12px; font-size:22px;">📋</td>
                    <td style="padding:12px;"><b>Step 2</b> — Copy and paste the job description you're applying for.</td>
                </tr>
                <tr style="background-color:#f0f5ff;">
                    <td style="padding:12px; font-size:22px;">🔍</td>
                    <td style="padding:12px;"><b>Step 3</b> — Click <b>Analyze Resume</b> to get your results instantly.</td>
                </tr>
                <tr>
                    <td style="padding:12px; font-size:22px;">📊</td>
                    <td style="padding:12px;"><b>Step 4</b> — Review your match score, skill gaps, and personalized suggestions.</td>
                </tr>
            </table>
        </div>

        <div style="display:flex; gap:16px; margin-top:10px;">
            <div class="card" style="flex:1; text-align:center; border-left-color:#27ae60;">
                <h3 style="color:#27ae60;">🎯 Smart Matching</h3>
                <p style="color:#666;">Compares your skills with job requirements using NLP keyword analysis.</p>
            </div>
            <div class="card" style="flex:1; text-align:center; border-left-color:#f39c12;">
                <h3 style="color:#f39c12;">📈 Gap Analysis</h3>
                <p style="color:#666;">Instantly identifies missing skills to help you improve your profile.</p>
            </div>
            <div class="card" style="flex:1; text-align:center; border-left-color:#0057b8;">
                <h3 style="color:#0057b8;">💡 AI Suggestions</h3>
                <p style="color:#666;">Get personalized recommendations based on your match score.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ── ANALYSIS ──
if analyze_btn:
    if not uploaded_file:
        st.warning("⚠️ Please upload a resume PDF in the sidebar.")
    elif not job_desc.strip():
        st.warning("⚠️ Please paste a job description in the sidebar.")
    else:
        with st.spinner("⚙️ Analyzing your resume, please wait..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            clean_resume = clean_text(resume_text)
            clean_job = clean_text(job_desc)
            resume_skills = extract_skills(clean_resume, SKILLS_DB)
            job_skills = extract_skills(clean_job, SKILLS_DB)
            match_pct, missing_skills = calculate_match(resume_skills, job_skills)
            suggestion = generate_suggestion(missing_skills, match_pct)

        # ── METRICS + GAUGE ──
        col1, col2, col3, col_gauge = st.columns([1, 1, 1, 2])
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <p>Match Score</p>
                    <h1>{match_pct}%</h1>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-card" style="background-color:#27ae60;">
                    <p>Skills in Resume</p>
                    <h1>{len(resume_skills)}</h1>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="metric-card" style="background-color:#e74c3c;">
                    <p>Missing Skills</p>
                    <h1>{len(missing_skills)}</h1>
                </div>
            """, unsafe_allow_html=True)
        with col_gauge:
            st.plotly_chart(make_gauge(match_pct), use_container_width=True)

        st.markdown("---")

        # ── SKILLS + MISSING ──
        left, right = st.columns(2)
        with left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">✅ Skills Found in Resume</p>', unsafe_allow_html=True)
            if resume_skills:
                badges = " ".join([f'<span class="badge-green">{s.title()}</span>' for s in resume_skills])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.info("No matching skills detected.")
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">❌ Missing Skills</p>', unsafe_allow_html=True)
            if missing_skills:
                badges = " ".join([f'<span class="badge-red">{s.title()}</span>' for s in missing_skills])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.success("No missing skills! Perfect match. 🎉")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── ANIMATED PROGRESS BAR ──
        st.markdown(f"""
            <div class="card">
                <p class="section-title">📊 Match Score Progress</p>
                <div class="progress-container">
                    <div style="
                        height: 100%;
                        border-radius: 10px;
                        background: linear-gradient(90deg, #0057b8, #00aaff);
                        width: 0%;
                        display: flex;
                        align-items: center;
                        justify-content: flex-end;
                        padding-right: 10px;
                        color: white;
                        font-size: 12px;
                        font-weight: 600;
                        animation: fillBar 1.5s ease-out forwards;
                    "></div>
                </div>
                <style>
                    @keyframes fillBar {{
                        from {{ width: 0%; }}
                        to {{ width: {match_pct}%; }}
                    }}
                </style>
            </div>
        """, unsafe_allow_html=True)

        # ── SUGGESTION ──
        st.markdown(f"""
            <div class="card" style="border-left-color:#f39c12;">
                <p class="section-title">💡 Recommendation</p>
                <p style="color:#444; font-size:15px;">{suggestion}</p>
            </div>
        """, unsafe_allow_html=True)

        # ── FOOTER ──
        st.markdown("""
            <div style="
                margin-top: 40px;
                padding: 20px;
                background: linear-gradient(90deg, #1a2a4a, #0057b8);
                border-radius: 12px;
                text-align: center;
            ">
                <p style="color:#cce0ff; margin:0; font-size:14px;">
                    🧠 <b style="color:white;">AI Resume Analyzer</b> &nbsp;|&nbsp; Built with Python & Streamlit
                </p>
                <p style="color:#99bbdd; margin:6px 0 0 0; font-size:13px;">
                    © 2026 <b style="color:white;">Shivani</b>. All rights reserved.
                </p>
            </div>
        """, unsafe_allow_html=True)