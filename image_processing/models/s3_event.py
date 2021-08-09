from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field


class GithubPage(BaseModel):
    page_name: str = Field(...)
    title: str = Field(...)
    summary: Optional[str] = Field(...)
    action: str = Field(...)
    sha: str = Field(...)
    html_url: AnyHttpUrl = Field(...)
