import json
import random
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from config import Config
from driver import setup_driver
from multiprocessing import Pool
from process import get_proxy_batch
from utils import get_accounts

def process_livestream(account, username, config: Config, comments, proxy=None):
    driver = setup_driver(account, headless=config.headless, proxy=proxy)
    driver.get(f'https://www.instagram.com/{username}')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, f'//img[@alt="{username}\'s profile picture"]'))
    ).click()
    time.sleep(3)
    input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//textarea[@aria-label="Add a comment…"]'))
    )
    input.click()
    input.send_keys(random.choice(comments))
    input.send_keys(Keys.ENTER)
    time.sleep(config.watch_time)

    driver.quit()

def livestream(config: Config):
    with Pool(config.accounts) as pool:
        with open('data/comments.json') as f:
            comments = json.load(f)['comments']
        accounts = get_accounts(config.accounts)
        proxies_batch = get_proxy_batch(config, len(accounts))
        args = [(account, config.target_username, config, comments, proxy) for account, proxy in zip(accounts, proxies_batch)]
        pool.starmap(process_livestream, args)

