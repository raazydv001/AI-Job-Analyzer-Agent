from models.schemas import JobAnalysis
from services.llm import create_llm


def analyze_job_description(job_description: str) -> JobAnalysis:

    if not job_description.strip():
        raise ValueError(
            "Job description cannot be empty."
        )

    llm = create_llm()

    structured_llm = llm.with_structured_output(
        JobAnalysis
    )

    prompt = f"""
You are an AI job description analyzer.

Analyze the following job description.

Extract only information that is actually present
in the job description.

Do not invent skills, experience, or responsibilities.

Job Description:
{job_description}
"""

    result = structured_llm.invoke(prompt)

    return result