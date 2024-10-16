import os
from selenium.webdriver import Chrome, ChromeOptions
import undetected_chromedriver as uc
import pickle
import logging
from utils import isSetup
from accounts import setup_profile
from utils import handle_notification_popup

logger = logging.getLogger(__name__)

def load_cookies(driver, email):
    with open(f'sessions/{email}.pkl', 'rb') as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()

# def login(driver, email):
    

def setup_driver(email, headless=False, proxy=None):
    options = ChromeOptions()
    if headless:
        options.add_argument('--headless')

    if proxy:
        if 'zip' in proxy:
            extension_path = f"{os.path.join(os.getcwd(), proxy.replace('.zip', ''))}"
            options.add_argument(f"--load-extension={extension_path}")
        else:
            options.add_argument(f"--proxy-server={proxy}")

    options.add_argument('--log-level=3')  # Suppress logs
    options.add_argument('--mute-audio')
    driver = uc.Chrome(options=options)
    driver.get('https://www.instagram.com/')

    if email:
        load_cookies(driver, email)
        if 'suspended' in driver.current_url:
            driver.quit()
            return None
        driver.email = email
        proxy_type = "Rotating" if proxy and "zip" in proxy else proxy
        logging.info(f'Logged in as {email} {f'| Proxy: {proxy_type}' if proxy else ""}')

        handle_notification_popup(driver)

        if not isSetup(email):
            setup_profile(driver)


    return driver
