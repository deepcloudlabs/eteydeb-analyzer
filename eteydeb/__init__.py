import logging
import time

from requests import Timeout, RequestException

from eteydeb.models import Project
from events import publish_event, NewProjectCreatedEvent, ProjectEventType, ProjectStatusChangedEvent
from persistence import project_collection
from utils_http import read_cookies

logging.info("eteydeb module is loaded.")

import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup

from utils_commons import clean_text as _clean_text

ETEYDEB_URL = "https://eteydeb.tubitak.gov.tr/firmakullanicisianasayfa.htm?mod=2"
COOKIE_FILE = "cookies.txt"

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "teydeb"
COLLECTION_NAME = "projects"

POLL_SECONDS = 60

STATUS_RE = re.compile(r"^(.*?)\s*Ticarileşme Durumu:\s*(.*)$", re.UNICODE)

logging.basicConfig(level=logging.INFO)


def retrieve_teydeb_project_history(url: str, cookies: str):
    logging.info(f"Retrieving project history from {url[:64]}...")
    try:
        response = requests.get(f"https://eteydeb.tubitak.gov.tr/{url}", headers={"Cookie": cookies}, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        history = [tr for tr in soup.select("table.veriListeTablo tbody tr")]
        for project_history_step in history:
            td_date, td_step = [td.get_text() for td in project_history_step.select("td")]
            logging.error(td_date, td_step)
        time.sleep(20)
    except Timeout:
        logging.error("Request timed out.")
    except RequestException as e:
        logging.error(f"Network/request error: {e}")
    except Exception as e:
        logging.error(f"An error has occurred: {e}")


def retrieve_teydeb_project_info(url: str, cookies: str):
    logging.info(f"Retrieving project info from {url[:64]}...")
    try:
        response = requests.get(url, headers={"Cookie": cookies}, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        all_links = [a.get("href") for a in soup.select("a[href]")]
        for link in all_links:
            if "javascript:void(openPopUp('basvurudurumgecmisi" in link:
                m = re.search(r"'([^']*)'", link)
                basvuru_durum_gecmisi = m.group(1) if m else None
                retrieve_teydeb_project_history(basvuru_durum_gecmisi, cookies)
        time.sleep(30)
    except Timeout:
        logging.error("Request timed out.")
    except RequestException as e:
        logging.error(f"Network/request error: {e}")
    except Exception as e:
        logging.error(f"An error has occurred: {e}")


def retrieve_teydeb_projects(cookies: str) -> list[Project]:
    project_list: list[Project] = []
    try:
        response = requests.get(ETEYDEB_URL, headers={"Cookie": cookies}, timeout=15)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        projects = [a for a in soup.select("table.veriListeTablo tr")[1:]]
        for project in projects:
            columns = [a for a in project.select("td")]
            no = int(_clean_text(columns[0].get_text()))
            project_code = int(_clean_text(columns[1].get_text()))
            support_type = _clean_text(columns[2].get_text())
            project_type = _clean_text(columns[3].get_text())
            application_date = _clean_text(columns[4].get_text())
            project_name = _clean_text(columns[5].get_text())
            project_owner = _clean_text(columns[6].get_text())
            project_status_column = columns[7].get_text().strip().replace("\n", "").replace("\r", "").strip()
            result = STATUS_RE.search(project_status_column)
            project_status = project_status_column
            project_commercialization_status = "N/A"
            project_info_ref = "https://eteydeb.tubitak.gov.tr/" + \
                               columns[9].select_one("a").get_attribute_list("href")[0]
            retrieve_teydeb_project_info(project_info_ref, cookies)

            if result:
                project_status = result.group(1)
                project_commercialization_status = result.group(2)
            teydeb_manager = _clean_text(columns[8].get_text())
            project_list.append(Project(
                project_code=project_code,
                project_name=project_name,
                support_type=support_type,
                project_type=project_type,
                application_date=application_date,
                project_owner=project_owner,
                project_status=project_status,
                project_commercialization_status=project_commercialization_status,
                teydeb_manager=teydeb_manager,
                updated_at=str(datetime.now()),
                created_at=str(datetime.now())
            ))
    except Timeout:
        logging.error("Request timed out.")
    except RequestException as e:
        logging.error(f"Network/request error: {e}")
    except Exception as e:
        logging.error(f"An error has occurred: {e}")
    return project_list


def poll_project_status():
    logging.info(f"Polling project status {datetime.now()}")
    projects = retrieve_teydeb_projects(read_cookies())
    logging.info(f"Found {len(projects)} projects.")
    projects_has_status_changed = []
    for project in projects:
        doc = project_collection.find_one({"project_code": project.project_code})
        if not doc:
            project_collection.insert_one(asdict(project))
            publish_event(
                NewProjectCreatedEvent(str(uuid.uuid4()), str(datetime.now()), ProjectEventType.NEW_PROJECT_CREATED,
                                       project))
        else:
            if doc["project_status"] != project.project_status:
                projects_has_status_changed.append(project)
                project_collection.update_one({"project_code": project.project_code},
                                              {"$set": {"project_status": project.project_status}})
                logging.info(
                    f"{project.project_code:7} {project.project_name[:32]:32} {project.support_type:24} {project.project_status:28} {project.project_commercialization_status:28} {project.teydeb_manager:24}")
                publish_event(
                    ProjectStatusChangedEvent(str(uuid.uuid4()), str(datetime.now()),
                                              ProjectEventType.PROJECT_STATUS_CHANGED,
                                              project))
    logging.info(f"Summary:")
    if len(projects_has_status_changed) > 0:
        logging.info(f"There is/are {len(projects_has_status_changed)} projects has status changed.")
    else:
        logging.info(f"There is NO change in the projects.")
