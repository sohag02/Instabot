import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
from utils import wait_for_page_load
import logging
import pandas as pd
import random
import os

logger = logging.getLogger(__name__)

def get_name(file="data/names.csv"):
    df = pd.read_csv(file)
    # Check if the DataFrame is empty (i.e., no rows are present)
    if df.empty:
        return None, None
    
    # Get the first row (excluding the header)
    first_row = df.iloc[0]
    
    # Drop the first row from the DataFrame
    df = df.drop(index=0)
    
    # Save the updated DataFrame back to the CSV file
    df.to_csv(file, index=False)
    
    # Extract the first name and last name
    firstname = first_row['firstname']
    lastname = first_row['lastname']
    gender = first_row['gender']
    
    return firstname, lastname, gender

def update_csv(profile, file="internal/setup.csv"):
    row = pd.DataFrame({'profile': [profile]}, index=[0])
    row.to_csv(file, mode='a', index=False, header=False)

def get_profile_pic(gender=None):
    photo_dir = "Photos"
    photos = os.listdir(photo_dir)

    if not photos:
        return None

    if gender is None:
        return os.path.join(os.getcwd(), photo_dir, photos[0])

    for photo in photos:
        if photo.startswith(gender):
            return os.path.join(os.getcwd(), photo_dir, photo)
    return None

def build_username(firstname, lastname):
    n = random.randint(0, 1000)
    return f'{firstname}.{lastname}.{n}'

def change_name(driver:Chrome, firstname, lastname):

    # Change name
    logging.info(f'Changing name for {driver.email}')
    
    label_element = driver.find_element(By.XPATH, "//label[text()='Name']")
    input_id = label_element.get_attribute("for")
    input_element = driver.find_element(By.ID, input_id)
    input_element.click()
    input_element.send_keys(Keys.CONTROL + 'a')
    input_element.send_keys(f'{firstname} {lastname}')
    btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="Done"]'))
    )
    
    # click with javascript
    driver.execute_script("arguments[0].click();", btn)
    logging.info(f'Successfully changed name for {driver.email} to {firstname} {lastname}')

def change_username(driver:Chrome, firstname, lastname):
    logging.info(f'Changing username for {driver.email}')
    label_element = driver.find_element(By.XPATH, "//label[text()='Username']")
    input_id = label_element.get_attribute("for")
    input_element = driver.find_element(By.ID, input_id)
    while True:
        username = build_username(firstname, lastname)
        input_element.click()
        input_element.send_keys(Keys.CONTROL + 'a')
        input_element.send_keys(username)
        print('sending')
        try:
            # parent = input_element.find_element(By.XPATH, '..')
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[local-name() = "svg" and @title="Input Username is valid."]'))
            )
            break
        except Exception as e:
            print(e.__class__.__name__)
            continue
    btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="Done"]'))
    )
    try:
        btn.click()
    except:
        # click with javascript
        driver.execute_script("arguments[0].click();", btn)
    logging.info(f'Successfully changed username for {driver.email} to {username}')
    # time.sleep(500)

def change_profile_pic(driver:Chrome, gender):
    logging.info(f'Changing profile pic for {driver.email}')
    photo = get_profile_pic() # TODO: Pass gender
    if not photo:
        logging.error('No profile pic found in folder')
        return
    
    file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    driver.execute_script("arguments[0].style.display = 'block';", file_input)
    file_input.send_keys(photo)

    btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="Save"]'))
    )

    try:
        btn.click()
    except:
        # click with javascript
        driver.execute_script("arguments[0].click();", btn)
    logging.info(f'Successfully changed profile pic for {driver.email}')



def setup_profile(driver:Chrome):
    driver.get('https://accountscenter.instagram.com/')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[contains(@aria-label, "Instagram")]'))
    ).click()
    wait_for_page_load(driver)
    time.sleep(2)
    url = driver.current_url
    firstname, lastname, gender = get_name()

    driver.get(f'{url}name/')
    wait_for_page_load(driver)
    change_name(driver, firstname, lastname)

    driver.get(f'{url}username/')
    wait_for_page_load(driver)
    change_username(driver, firstname, lastname)

    driver.get(f'{url}photo/')
    wait_for_page_load(driver)
    change_profile_pic(driver, gender)

    update_csv(driver.email)
    logging.info(f'Successfully setup profile for {driver.email}')