import streamlit as st

from services.job_analyzer import analyze_job_description


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
# Only CSS here — NO HTML UI elements
# ============================================================

st.markdown(
    """
    <style>

    /* Main app */
    .stApp {
        background-color: #0b1020;
    }

    [data-testid="stAppViewContainer"] > .main {
        padding: 2rem 4rem 4rem 4rem;
    }

    /* Main title */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .main-subtitle {
        font-size: 17px;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    /* Section headings */
    .section-heading {
        font-size: 21px;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    /* Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        background-color: rgba(15, 23, 42, 0.65);
    }

    /* Analyze button */
    .stButton > button {
        border-radius: 12px;
        font-size: 16px;
        font-weight: 700;
        height: 3rem;
    }

    /* Text area */
    textarea {
        border-radius: 14px !important;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🎯 AI Job Analyzer</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="main-subtitle">
    Analyze job descriptions using AI and instantly understand
    the role, skills, experience requirements and responsibilities.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INPUT SECTION
# ============================================================

with st.container(border=True):

    st.subheader("📋 Job Description")

    st.caption(
        "Paste the complete job description below."
    )

    job_description = st.text_area(
        "Job Description",
        height=280,
        label_visibility="collapsed",
        placeholder=(
            "Example:\n\n"
            "We are looking for a Java Software Engineer...\n\n"
            "Required Skills:\n"
            "Java, Spring Boot, SQL, AWS..."
        )
    )

    analyze_button = st.button(
        "🚀 Analyze Job Description",
        use_container_width=True
    )


# ============================================================
# ANALYSIS
# ============================================================

if analyze_button:

    if not job_description.strip():

        st.warning(
            "⚠️ Please paste a job description first."
        )

    else:

        try:

            with st.spinner(
                "🤖 AI is analyzing the job description..."
            ):

                result = analyze_job_description(
                    job_description
                )

            st.success(
                "✅ Analysis completed successfully!"
            )


            # ==================================================
            # JOB ROLE
            # ==================================================

            st.markdown(
                '<div class="section-heading">💼 Job Role</div>',
                unsafe_allow_html=True
            )

            with st.container(border=True):

                st.title(
                    result.job_title
                )


            # ==================================================
            # SKILLS
            # ==================================================

            st.markdown(
                '<div class="section-heading">🧠 Skills</div>',
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)

            # --------------------------------------------------
            # REQUIRED SKILLS
            # --------------------------------------------------

            with col1:

                with st.container(border=True):

                    st.subheader(
                        "✅ Required Skills"
                    )

                    if result.required_skills:

                        for skill in result.required_skills:
                            st.markdown(
                                f"• **{skill}**"
                            )

                    else:

                        st.info(
                            "No required skills identified."
                        )


            # --------------------------------------------------
            # PREFERRED SKILLS
            # --------------------------------------------------

            with col2:

                with st.container(border=True):

                    st.subheader(
                        "⭐ Preferred Skills"
                    )

                    if result.preferred_skills:

                        for skill in result.preferred_skills:
                            st.markdown(
                                f"• **{skill}**"
                            )

                    else:

                        st.info(
                            "No preferred skills identified."
                        )


            # ==================================================
            # EXPERIENCE
            # ==================================================

            st.markdown(
                '<div class="section-heading">🧑‍💻 Experience</div>',
                unsafe_allow_html=True
            )

            with st.container(border=True):

                st.info(
                    result.experience
                )


            # ==================================================
            # RESPONSIBILITIES
            # ==================================================

            st.markdown(
                '<div class="section-heading">🛠 Responsibilities</div>',
                unsafe_allow_html=True
            )

            with st.container(border=True):

                if result.responsibilities:

                    for index, responsibility in enumerate(
                        result.responsibilities,
                        start=1
                    ):

                        st.markdown(
                            f"**{index}.** {responsibility}"
                        )

                        if index != len(result.responsibilities):
                            st.divider()

                else:

                    st.info(
                        "No responsibilities identified."
                    )


        except Exception as e:

            st.error(
                f"Something went wrong: {str(e)}"
            )