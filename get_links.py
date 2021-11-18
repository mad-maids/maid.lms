"""
Scrapes the intranet LMS section. Gets all the links for all the files and
saves them in a corresponding .json file in the data folder.
"""

import datetime as dt
import json
import logging
import random
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

from environs import Env
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

IGNORED_EXCEPTIONS = (
    NoSuchElementException,
    StaleElementReferenceException,
)


logging.basicConfig(level=logging.INFO, format="#%(levelname)-8s %(message)s")

env = Env()
env.read_env()

# Workflow is failing if the browser window is not maximized.
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# these are saved in the .env file
USER_ID = env.str("USER_ID")
PASSWORD = env.str("PASSWORD")

# create an instance of and launch chrome webdriver
browser = webdriver.Chrome(options=chrome_options)

# make a GET request to intranet timetable
browser.get("https://intranet.wiut.uz/UserModuleMaterials")

# filling in user id
userid_field = browser.find_element(
    By.XPATH, "/html/body/div[2]/div[2]/div[2]/section/form/fieldset/div[1]/div/input"
)
userid_field.click()
userid_field.send_keys(USER_ID)

# filling in password
password_field = browser.find_element(
    By.XPATH, "/html/body/div[2]/div[2]/div[2]/section/form/fieldset/div[2]/div/input"
)
password_field.click()
password_field.send_keys(PASSWORD)
password_field.send_keys(Keys.ENTER)

# these contain the links to the module pages
module_paragraphs = browser.find_elements(By.CLASS_NAME, value="panel-text")

module_links = []

for paragraph in module_paragraphs:
    module_link = paragraph.find_element(
        By.TAG_NAME,
        value="a",
    ).get_attribute("href")

    module_links.append(module_link)

for module_link in module_links:
    browser.get(module_link)

    name_span = browser.find_element(By.ID, value="spanModuleName")
    module_name = name_span.text.split(" - ")[-1]

    logging.info(f"MODULE: {module_name}")

    # when the year is changed on one module page, it's changed on all pages
    # so first check the current academic year
    month = dt.date.today().month
    year = dt.date.today().year

    if month > 8:
        text = f"Academic Year {year}/{year+1}"
    else:
        text = f"Academic Year {year-1}/{year}"

    select = Select(
        WebDriverWait(browser, 15, ignored_exceptions=IGNORED_EXCEPTIONS).until(
            EC.presence_of_element_located((By.ID, "LMSAcadYear"))
        )
    )
    select.select_by_visible_text(text)

    # data that will be dumped to a json file
    data: Dict[str, Any] = {"year": "current"}

    section_divs = browser.find_elements(By.CLASS_NAME, value="group")

    # no materials are available on this page for this academic year
    if not section_divs:

        select = Select(
            WebDriverWait(browser, 15, ignored_exceptions=IGNORED_EXCEPTIONS).until(
                EC.presence_of_element_located((By.ID, "LMSAcadYear"))
            )
        )

        # get the previous year option text
        previous_year = None
        for index, option in enumerate(select.options):
            if option.get_attribute("selected"):
                previous_year = select.options[index - 1].text

        select.select_by_visible_text(previous_year)

        data["year"] = "previous"

        section_divs = browser.find_elements(By.CLASS_NAME, value="group")

    for div in section_divs:
        section = div.text
        logging.info(f"Going through {section}")

        # scroll down to element (prevents ElementNotInteractableException)
        ActionChains(browser).move_to_element(div).perform()

        # in one module, there is a useless div that cant be clicked
        try:
            div.click()
        except ElementNotInteractableException:
            continue

        # wait for links to appear (uls have the links)
        WebDriverWait(div, 15, ignored_exceptions=IGNORED_EXCEPTIONS).until(
            EC.presence_of_element_located((By.TAG_NAME, "ul"))
        )

        links = div.find_elements(By.TAG_NAME, value="a")

        materials = dict()
        for link in links:
            file_name = link.text
            file_link = link.get_attribute("href")

            # one material in qm module has an a tag with no href
            # the first link in the div is usually a dead link
            if not file_link or file_link[-1] == "#":
                continue

            materials[file_name] = file_link

        data[section] = materials

    # no links were found
    if len(data.keys()) == 1:
        continue

    # creating the relevant dir if it doesn't exit
    Path(f"./data").mkdir(parents=True, exist_ok=True)

    with open(f"./data/{module_name}.json", "w") as output:
        # indent is indicated to apply pretty formatting
        json.dump(data, output, indent=2)

    # to be on the safe side and not send a ton of requests in a short time
    # random is used so that it seems like a human is actually doing this
    time.sleep(random.uniform(2, 3))

browser.quit()

# run prettier formatter in the end
subprocess.run(["yarn", "install"])
script = "yarn format:check --write"
command = script.split()
subprocess.run(command)

