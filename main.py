#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import time
import os
from os import path

LOGIN_URL = "https://moodle.ktu.edu/login/index.php"
EDIT_ASSIGNMENT_URL = "https://moodle.ktu.edu/mod/assign/view.php?id=1499&action=editsubmission"

moodle_filename = "IF-1-1_Rokas_Puzonas.pdf"
filename = "report.pdf"

def main():
    load_dotenv()

    options = Options()
    # options.headless = True
    driver = webdriver.Firefox(options=options)

    driver.get(LOGIN_URL)
    driver.find_element(By.ID, "username").send_keys(os.environ["KTU_USERNAME"])
    driver.find_element(By.ID, "password").send_keys(os.environ["KTU_PASSWORD"])
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    time.sleep(1)

    driver.find_element(By.ID, "yesbutton").click()
    time.sleep(1)

    driver.get(EDIT_ASSIGNMENT_URL)
    time.sleep(1)

    file = driver.find_element(By.XPATH, f"//*[text()='{moodle_filename}']")
    if file:
        file.click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[text()='Naikinti']").click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[contains(@class, 'fp-dlg-butconfirm')]").click()
        time.sleep(1)

    driver.find_element(By.CLASS_NAME, "filemanager-container").click()
    time.sleep(1)

    driver.find_element(By.XPATH, "//input[@type='file']").send_keys(path.abspath(filename))
    driver.find_element(By.XPATH, "//input[@name='title']").send_keys(moodle_filename)
    driver.find_element(By.CLASS_NAME, "fp-upload-btn").click()
    time.sleep(1)

    driver.find_element(By.ID, "id_submitbutton").click()

    driver.close()

if __name__ == "__main__":
    main()

