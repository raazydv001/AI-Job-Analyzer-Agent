import streamlit as st

from services.job_analyzer import analyze_job_description
from services.resume_parser import extract_resume_text
from services.resume_rag import (
    split_resume_text,
    create_resume_vector_store,
    search_resume
)


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

    .section-title {
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 10px;
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
            using RAG-powered resume search.
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
        help="Maximum size: 5 MB."
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

                st.session_state[
                    "resume_text"
                ] = resume_text

                st.session_state[
                    "resume_filename"
                ] = uploaded_resume.name

                # Reset RAG status because a new extraction
                # may represent a different resume.
                st.session_state[
                    "rag_ready"
                ] = False

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
# RESUME TEXT
# ============================================================

if "resume_text" in st.session_state:

    st.divider()

    st.markdown(
        "### 📃 Extracted Resume Text"
    )

    st.caption(
        f"Source: "
        f"{st.session_state.get('resume_filename', 'Resume')}"
    )

    resume_text = st.session_state[
        "resume_text"
    ]

    with st.expander(
        "View extracted text",
        expanded=False
    ):

        st.text_area(
            "Extracted content",
            value=resume_text,
            height=400,
            label_visibility="collapsed"
        )

    word_count = len(
        resume_text.split()
    )

    character_count = len(
        resume_text
    )

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
# BUILD RESUME RAG
# ============================================================

if "resume_text" in st.session_state:

    st.divider()

    st.markdown(
        "### 🧠 Resume RAG"
    )

    st.write(
        "Convert the extracted resume text into searchable "
        "chunks and store their embeddings in ChromaDB."
    )

    build_rag_button = st.button(
        "⚡ Build Resume RAG",
        use_container_width=True
    )

    if build_rag_button:

        try:

            with st.spinner(
                "Splitting resume and creating embeddings..."
            ):

                chunks = split_resume_text(
                    resume_text=st.session_state[
                        "resume_text"
                    ],
                    filename=st.session_state.get(
                        "resume_filename",
                        "resume"
                    )
                )

                create_resume_vector_store(
                    chunks
                )

            st.session_state[
                "rag_ready"
            ] = True

            st.session_state[
                "chunk_count"
            ] = len(chunks)

            st.success(
                "Resume RAG created successfully."
            )

            st.info(
                f"Created {len(chunks)} resume chunks "
                "and stored their embeddings in ChromaDB."
            )

        except ValueError as e:

            st.error(str(e))

        except Exception as e:

            st.error(
                f"Error while creating Resume RAG: {str(e)}"
            )


# ============================================================
# SHOW CHUNK COUNT
# ============================================================

if st.session_state.get(
    "rag_ready",
    False
):

    chunk_count = st.session_state.get(
        "chunk_count",
        0
    )

    st.success(
        f"🟢 Resume RAG is ready — "
        f"{chunk_count} chunks stored."
    )


# ============================================================
# TEST RESUME RETRIEVER
# ============================================================
# ============================================================
# TEST RESUME RETRIEVER
# ============================================================

if st.session_state.get("rag_ready", False):

    st.divider()

    st.markdown("### 🔎 Test Resume Search")

    st.write(
        "Ask a question about the resume. "
        "The retriever will return the most relevant chunks."
    )

    search_query = st.text_input(
        "Resume search query",
        placeholder=(
            "Example: What experience does the candidate "
            "have with Java?"
        )
    )

    search_button = st.button(
        "🔍 Search Resume",
        use_container_width=True
    )

    if search_button:

        if not search_query.strip():

            st.warning(
                "Please enter a search query."
            )

        else:

            try:

                with st.spinner(
                    "Searching resume..."
                ):

                    results = search_resume(
                        query=search_query,
                        k=3
                    )

                if not results:

                    st.warning(
                        "No relevant resume chunks found."
                    )

                else:

                    st.success(
                        f"Found {len(results)} relevant chunks."
                    )

                    # results = [(Document, score), ...]
                    for index, (document, score) in enumerate(
                        results,
                        start=1
                    ):

                        st.markdown(
                            f"#### Result {index}"
                        )

                        source = document.metadata.get(
                            "source",
                            "Unknown"
                        )

                        chunk_id = document.metadata.get(
                            "chunk_id",
                            "Unknown"
                        )

                        st.caption(
                            f"Source: {source} | "
                            f"Chunk: {chunk_id} | "
                            f"Distance: {score:.4f}"
                        )

                        st.write(
                            document.page_content
                        )

                        st.divider()

            except ValueError as e:

                st.error(
                    str(e)
                )

            except Exception as e:

                st.error(
                    f"Resume search failed: {str(e)}"
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

            st.markdown(
                "### 💼 Job Role"
            )

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

            st.error(
                str(e)
            )

        except Exception as e:

            st.error(
                f"Something went wrong: {str(e)}"
            )