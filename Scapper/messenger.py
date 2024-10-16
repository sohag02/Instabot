import os
from driver import setup_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import logging
import time
from config import Config
import csv
import json
import random

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)-5s - %(message)s')

def send_message(driver, message, username):
    driver.get(f'https://www.instagram.com/{username}/')
    try:
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//div[text()="Message" and @role="button"]'))
            ).click()
        except Exception:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Options"]'))
            ).click()

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="Send message"]'))
            ).click()

        msg_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Message"]'))
        )
        msg_box.click()
        msg_box.send_keys(message)
        msg_box.send_keys(Keys.ENTER)
        time.sleep(2)
        logging.info(f'Sent message to @{username} with {driver.email} : {message}')
        return True
    except Exception as e:
        logging.error(f'Failed to send message to @{username} with {driver.email}')
        return False
    
def handle_notification_popup(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Not Now"]'))
        ).click()
    except Exception:
        pass

if __name__ == '__main__':
    config = Config()
    sessions = os.listdir('sessions')
    if not sessions:
        logging.error('No sessions found in sessions folder')
        exit()

    if len(sessions) < config.accounts:
        logging.error(f'Not enough sessions found in sessions folder. Found {len(sessions)} sessions, but need {config.accounts}')
        exit()

    sessions = sessions[:config.accounts]
    with open(config.username_file, 'r') as f:
        usernames = csv.reader(f)
        usernames = [row[0] for row in usernames]

    with open(config.msg_file, 'r') as f:
        data = json.load(f)
        messages = data['messages']

    count = 0
    for session in sessions:
        driver = setup_driver(session.replace('.pkl', ''), headless=config.headless)
        driver.get('https://www.instagram.com/')
        handle_notification_popup(driver)
        time.sleep(2)
        for username in usernames:
            res = send_message(driver, random.choice(messages), username)
            if res:
                count += 1
        driver.quit()
    logging.info(f'Successfully sent {count} messages')


