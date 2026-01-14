import logging
import time

from eteydeb import poll_project_status

logging.basicConfig(level=logging.INFO)

POLL_SECONDS = 10

while True:
    poll_project_status()
    time.sleep(POLL_SECONDS)