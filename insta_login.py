from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import csv
import pickle
import time
import os

def wait_for_page_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def login_instagram(driver: Chrome, username, password):
    driver.get('https://www.instagram.com/')
    init_url = driver.current_url
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[aria-label="Phone number, username, or email"]'))
    ).send_keys(username)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '[aria-label="Password"]'))
    ).send_keys(password)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[type="submit"]'))
    ).click()
    time.sleep(5)
    if driver.current_url == init_url:
        print(f'Incorect email or password for {username}')
        return

    if 'suspended' in driver.current_url:
        print(f'Login failed for @{username}. Account is suspended.')
        return
    
    if 'onetap' in driver.current_url:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[text()="Not now" and @role="button"]'))
        ).click()
        wait_for_page_load(driver)


    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[aria-label="Home"]'))
        )
    except Exception:
        print(f'Login failed for {username}')
        return

    cookies = driver.get_cookies()
    with open(f'sessions_new/{username}.pkl', 'wb') as f:
        pickle.dump(cookies, f)
    print(f'Session generated for {username}')

if __name__ == '__main__':
    os.makedirs('sessions_new', exist_ok=True)
    options = ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--log-level=3')  # Suppress logs
    
    driver = Chrome(options=options)

    
    with open('data/gmail.csv', 'r') as f:
        accounts = csv.reader(f)
        next(accounts)  # Skip header

        for row in accounts:
            username = row[0]
            password = row[1]
            login_instagram(driver, username, password)
            driver.delete_all_cookies()
            driver.refresh()

    driver.quit()
