import streamlit as st

from services.job_analyzer import analyze_job_description
from services.resume_parser import extract_resume_text


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Job Analyzer",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1.5rem;
    }

    .hero {
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        background: linear-gradient(
            135deg,
            #111827,
            #312e81
        );
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: white;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 17px;
        color: #d1d5db;
        line-height: 1.6;
    }

    .card {
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #374151;
        background: rgba(31, 41, 55, 0.4);
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .skill-pill {
        display: inline-block;
        padding: 6px 12px;
        margin: 4px;
        border-radius: 20px;
        border: 1px solid #4b5563;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🎯 AI Job Analyzer
        </div>

        <div class="hero-subtitle">
            Analyze your resume against a job description
            and understand what the role expects.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TWO COLUMN LAYOUT
# ============================================================

resume_col, job_col = st.columns(
    [1, 1],
    gap="large"
)


# ============================================================
# RESUME SECTION
# ============================================================

with resume_col:

    st.markdown(
        '<div class="section-title">'
        '📄 Your Resume'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded_resume = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"],
        accept_multiple_files=False,
        help="Upload a PDF or DOCX resume. Maximum size: 5 MB."
    )

    if uploaded_resume:

        st.caption(
            f"📎 {uploaded_resume.name} • "
            f"{uploaded_resume.size / 1024:.1f} KB"
        )

        extract_button = st.button(
            "📖 Extract Resume Text",
            use_container_width=True
        )

        if extract_button:

            try:

                with st.spinner(
                    "Reading your resume..."
                ):

                    resume_text = extract_resume_text(
                        uploaded_resume
                    )

                # Save extracted text in Streamlit session
                st.session_state["resume_text"] = resume_text
                st.session_state["resume_filename"] = (
                    uploaded_resume.name
                )

                st.success(
                    "Resume text extracted successfully."
                )

            except ValueError as e:

                st.error(str(e))

            except Exception as e:

                st.error(
                    f"Unexpected error while processing "
                    f"the resume: {str(e)}"
                )


# ============================================================
# JOB DESCRIPTION SECTION
# ============================================================

with job_col:

    st.markdown(
        '<div class="section-title">'
        '💼 Job Description'
        '</div>',
        unsafe_allow_html=True
    )

    job_description = st.text_area(
        "Paste the job description",
        height=250,
        placeholder=(
            "Example:\n\n"
            "We are looking for a Java Software Engineer...\n"
            "Required skills: Java, Spring Boot, SQL, AWS..."
        )
    )

    analyze_button = st.button(
        "🚀 Analyze Job Description",
        use_container_width=True
    )


# ============================================================
# EXTRACTED RESUME TEXT
# ============================================================

if "resume_text" in st.session_state:

    st.divider()

    st.markdown(
        "### 📃 Extracted Resume Text"
    )

    st.caption(
        f"Source: {st.session_state.get('resume_filename', 'Resume')}"
    )

    resume_text = st.session_state["resume_text"]

    with st.expander(
        "View full extracted text",
        expanded=True
    ):

        st.text_area(
            "Extracted content",
            value=resume_text,
            height=450,
            label_visibility="collapsed"
        )

    # Simple statistics
    word_count = len(resume_text.split())
    character_count = len(resume_text)

    stat1, stat2 = st.columns(2)

    with stat1:
        st.metric(
            "Words",
            f"{word_count:,}"
        )

    with stat2:
        st.metric(
            "Characters",
            f"{character_count:,}"
        )


# ============================================================
# JOB ANALYSIS
# ============================================================

if analyze_button:

    if not job_description.strip():

        st.warning(
            "Please paste a job description first."
        )

    else:

        try:

            with st.spinner(
                "Analyzing job description..."
            ):

                result = analyze_job_description(
                    job_description
                )

            st.success(
                "Job description analyzed successfully!"
            )

            st.divider()

            # ------------------------------------------------
            # JOB TITLE
            # ------------------------------------------------

            st.markdown("### 💼 Job Role")

            st.markdown(
                f"## {result.job_title}"
            )

            # ------------------------------------------------
            # SKILLS
            # ------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "### ✅ Required Skills"
                )

                if result.required_skills:

                    for skill in result.required_skills:

                        st.markdown(
                            f"- {skill}"
                        )

                else:

                    st.write(
                        "No required skills identified."
                    )

            with col2:

                st.markdown(
                    "### ⭐ Preferred Skills"
                )

                if result.preferred_skills:

                    for skill in result.preferred_skills:

                        st.markdown(
                            f"- {skill}"
                        )

                else:

                    st.write(
                        "No preferred skills identified."
                    )

            # ------------------------------------------------
            # EXPERIENCE
            # ------------------------------------------------

            st.markdown(
                "### 🧑‍💻 Experience"
            )

            st.info(
                result.experience
            )

            # ------------------------------------------------
            # RESPONSIBILITIES
            # ------------------------------------------------

            st.markdown(
                "### 🛠 Responsibilities"
            )

            if result.responsibilities:

                for responsibility in result.responsibilities:

                    st.markdown(
                        f"- {responsibility}"
                    )

            else:

                st.write(
                    "No responsibilities identified."
                )

        except ValueError as e:

            st.error(str(e))

        except Exception as e:

            st.error(
                f"Something went wrong: {str(e)}"
            )