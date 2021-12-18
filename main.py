#!/usr/bin/env python
from selenium import webdriver
import click
from dotenv import load_dotenv
import time
from os import path
from typing import Optional

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

load_dotenv()

LOGIN_URL = "https://moodle.ktu.edu/login/index.php"
EDIT_ASSIGNMENT_URL = "https://moodle.ktu.edu/mod/assign/view.php?id={id}&action=editsubmission"

DEFAULT_TIMEOUT = 5

def create_driver() -> WebDriver:
    options = Options()
    options.headless = True
    return webdriver.Firefox(options=options)

def waited_find_element(
        driver: WebDriver,
        by: str,
        value: str,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Optional[WebElement]:
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        return None

def waited_find_elements(
        driver: WebDriver,
        by: str,
        value: str,
        timeout: int = DEFAULT_TIMEOUT
    ) -> list[WebElement]:
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
    except TimeoutException:
        return []

def assert_element(
        error_msg: str,
        driver: WebDriver,
        by: str,
        value: str,
        timeout: int = DEFAULT_TIMEOUT
    ) -> WebElement:
    element = waited_find_element(driver, by, value, timeout)
    if not element:
        raise NoSuchElementException(error_msg)
    return element

def login(driver: WebDriver, username: str, password: str):
    driver.get(LOGIN_URL)

    assert_element("Failed to select username field", driver, By.ID, "username").send_keys(username)
    assert_element("Failed to select password field", driver, By.ID, "password").send_keys(password)
    assert_element("Failed to select login submit button", driver, By.XPATH, "//input[@type='submit']").click()

    assert_element("Failed to select yes button in login", driver, By.ID, "yesbutton").click()
    time.sleep(1)

def upload_file_to_assignment(driver: WebDriver, assignment_id: str, filename: str, upload_filename: str):
    if not upload_filename:
        upload_filename = path.basename(filename)

    driver.get(EDIT_ASSIGNMENT_URL.format(id=assignment_id))

    # Check if files exists in assignment
    for file_elem in waited_find_elements(driver, By.XPATH, "//*[contains(@class, 'fp-file')]/*[contains(@class, 'd-block')]"):
        # If it does, delete it
        time.sleep(1)
        file_elem.click()
        assert_element("Failed to press delete file button", driver, By.CLASS_NAME, "fp-file-delete").click()
        assert_element("Failed to press confirm deletion file button", driver, By.CLASS_NAME, "fp-dlg-butconfirm").click()
    time.sleep(1)

    assert_element("Failed to click on file manager", driver, By.CLASS_NAME, "dndupload-arrow").click()
    assert_element("Failed to select file upload from computer", driver, By.XPATH, "//*[contains(@class, 'fp-repo-area')]/*[contains(@class, 'fp-repo')][2]").click()
    assert_element("Failed to specify upload file", driver, By.XPATH, "//input[@type='file']").send_keys(path.abspath(filename))
    assert_element("Failed to specify uploaded files name", driver, By.XPATH, "//input[@name='title']").send_keys(upload_filename)
    assert_element("Failed to press upload file button", driver, By.CLASS_NAME, "fp-upload-btn").click()
    time.sleep(1)

    assert_element("Failed to press submit files button", driver, By.ID, "id_submitbutton").click()

@click.command()
@click.argument("assignment")
@click.argument("filename", type=click.Path(exists=True, readable=True, dir_okay=False))
@click.argument("upload_filename", required=False, type=click.Path())
@click.option("--username", "-u", required=True, envvar="KTU_USERNAME")
@click.option("--password", "-p", required=True, envvar="KTU_PASSWORD")
def main(assignment, filename, upload_filename, username, password):
    driver = create_driver()

    login(driver, username, password)
    upload_file_to_assignment(driver, assignment, filename, upload_filename)

    driver.close()

if __name__ == "__main__":
    main()

