from pydantic import BaseModel, Field


class JobAnalysis(BaseModel):
    job_title: str = Field(
        description="The main job title mentioned in the job description."
    )

    required_skills: list[str] = Field(
        description="Skills that are explicitly required for the job."
    )

    preferred_skills: list[str] = Field(
        description="Skills mentioned as preferred, optional, or nice-to-have."
    )

    experience: str = Field(
        description="Required experience level mentioned in the job description."
    )

    responsibilities: list[str] = Field(
        description="Main responsibilities mentioned in the job description."
    )