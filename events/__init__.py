import logging
from dataclasses import dataclass
from enum import Enum
from eteydeb.models import Project

import winsound

logging.basicConfig(level=logging.INFO)

logging.info("eteydeb::events module is loaded.")


class ProjectEventType(Enum):
    PROJECT_STATUS_CHANGED = 10
    NEW_PROJECT_CREATED = 20


@dataclass(frozen=True)
class ProjectEvent:
    id: str
    timestamp: str
    eventType: ProjectEventType
    project: Project


@dataclass(frozen=True)
class ProjectStatusChangedEvent(ProjectEvent):
    pass


@dataclass(frozen=True)
class NewProjectCreatedEvent(ProjectEvent):
    pass


def publish_event(project_event: ProjectEvent) -> bool:
    if isinstance(project_event, ProjectStatusChangedEvent):
        logging.info(
            f"Project {project_event.project.project_code} status has changed to {project_event.project.project_status}")
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        return True
    elif isinstance(project_event, NewProjectCreatedEvent):
        logging.info(f"New project has been created: {project_event.project}")
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        return True
    return False
