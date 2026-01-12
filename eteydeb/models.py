from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    project_code: int
    project_name: str
    support_type: str
    project_type: str
    application_date: str
    project_owner: str
    project_status: str
    project_commercialization_status: str
    teydeb_manager: str
    created_at: str
    updated_at: str


