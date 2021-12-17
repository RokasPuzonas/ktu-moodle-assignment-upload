#!/usr/bin/env python
from selenium import webdriver
import click
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import time
from os import path

load_dotenv()

LOGIN_URL = "https://moodle.ktu.edu/login/index.php"
EDIT_ASSIGNMENT_URL = "https://moodle.ktu.edu/mod/assign/view.php?id={id}&action=editsubmission"

def create_driver() -> WebDriver:
    options = Options()
    options.headless = True
    return webdriver.Firefox(options=options)

def login(driver: WebDriver, username, password):
    driver.get(LOGIN_URL)

    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    time.sleep(1)

    driver.find_element(By.ID, "yesbutton").click()
    time.sleep(1)

def safe_find_element(driver, *args, **kvargs):
    try:
        return driver.find_element(*args, **kvargs)
    except NoSuchElementException:
        return None

def upload_file_to_assignment(driver: WebDriver, assignment, filename, upload_filename):
    if not upload_filename:
        upload_filename = path.basename(filename)

    driver.get(EDIT_ASSIGNMENT_URL.format(id=assignment))
    time.sleep(1)

    # Check if file exists
    file = safe_find_element(driver, By.XPATH, f"//*[text()='{upload_filename}']")
    if file:
        # If it does, delete it
        file.click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[text()='Naikinti']").click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(@class, 'fp-dlg-butconfirm')]").click()
        time.sleep(1)

    driver.find_element(By.CLASS_NAME, "filemanager-container").click()
    time.sleep(1)

    driver.find_element(By.XPATH, "//input[@type='file']").send_keys(path.abspath(filename))
    driver.find_element(By.XPATH, "//input[@name='title']").send_keys(upload_filename)
    driver.find_element(By.CLASS_NAME, "fp-upload-btn").click()
    time.sleep(1)

    driver.find_element(By.ID, "id_submitbutton").click()

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

