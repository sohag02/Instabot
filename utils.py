import itertools
import os
import random
import time
from typing import List
from instaloader import Instaloader, Profile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import logging
import csv
import pandas as pd
import requests
import pickle
import json

logger = logging.getLogger(__name__)


def scroll_down(driver: Chrome):
    driver.execute_script("window.scrollBy(0, 500);")


def scroll_up(driver):
    driver.execute_script("window.scrollTo(0, 0);")


def wait_for_page_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def get_links(driver: Chrome, username, range, type=None, log=True):
    if log:
        logging.info(f'Fetching {type if type else ''} links for {username}')

    url = '/'  # Default value
    if type == 'reel':
        driver.get(f'https://www.instagram.com/{username}/reels/')
        url = f'/{username}/reel/'
    elif type == 'photo' or type is None:
        driver.get(f'https://www.instagram.com/{username}/')
        url = '/p/'

    xpath = '//a[contains(@href, "/p/") or contains(@href, "/reel/")]' if type is None else f'//a[contains(@href, "{
        url}")]'

    wait_for_page_load(driver)
    time.sleep(2)
    links = []
    max_scroll_attempts = 10
    scroll_attempts = 0

    while scroll_attempts < max_scroll_attempts:
        try:
            elems = driver.find_elements(By.XPATH, xpath)
            if len(elems) >= range:
                break
            scroll_down(driver)
            time.sleep(2)
            scroll_attempts += 1
        except Exception as e:
            logging.error(f"Error finding links for {username}")
            return []

    for elem in elems[:range]:
        links.append(elem.get_attribute('href'))

    if log:
        logging.info(f'Successfully fetched {len(links)} {
                     type} links for {username}')
    return links


def get_random_session():
    sessions = os.listdir('sessions')
    if not sessions:
        return None
    return random.choice(sessions)


def get_share_usernames():
    with open('usernames.csv') as f:
        reader = csv.reader(f)
        usernames = [row[0] for row in reader]
        return usernames


def isSetup(profile):
    if not os.path.exists("internal/setup.csv"):
        return False

    df = pd.read_csv("internal/setup.csv")
    if df.empty:
        return False
    return profile in df['emails'].tolist()


def get_proxies() -> List[str]:
    with open("internal/working_proxies.txt", "r") as f:
        return f.readlines()


def get_accounts(count: int):
    sessions = os.listdir('sessions')
    sessions = list(map(lambda acc: acc.replace('.pkl', ''), sessions))

    if not sessions:
        logging.error(
            'No sessions found in Folder. Please run login.py first.')
        return

    accounts = random.sample(sessions, count)
    return accounts


def is_empty(generator):
    generator, check = itertools.tee(generator)
    try:
        next(check)
        return False
    except StopIteration:
        return True


def extract_user_id_from_cookies(cookies):
    for cookie in cookies:
        if cookie['name'] == 'ds_user_id':
            return cookie['value']
    return None


def get_first_elem(generator):
    try:
        return next(generator)
    except StopIteration:
        return None


def convert_cookies(selenium_cookies):
    """Converts selenium cookies to instaloader cookies"""
    session = requests.Session()
    for cookie in selenium_cookies:
        session.cookies.set(
            cookie['name'], cookie['value'], domain=cookie['domain'])
    return session.cookies.get_dict()


def login(context: Instaloader, session_file):
    with open(session_file, 'rb') as f:
        selenium_cookies = pickle.load(f)
    # Extract user ID from cookies
    user_id = extract_user_id_from_cookies(selenium_cookies)
    if not user_id:
        raise ValueError("Could not extract user ID from session cookies")

    instaloader_session = convert_cookies(selenium_cookies)

    # Load the session
    context.context.user_id = user_id
    context.context.username = user_id
    context.context._session.cookies.update(instaloader_session)

def get_stories(username):
    try:
        L = Instaloader()

        # Load and convert the session
        session = 'jessica.brown.202121@gmail.com.pkl'#get_random_session() #TODO: change this
        print(session)
        logging.info(f"Using session {session} to fetch stories for {username}")
        if not session:
            logging.error('No session found. Please run login.py first.')
            return
        session_file = f'sessions/{session}'

        login(L, session_file)

        profile = Profile.from_username(L.context, username)
        stories = L.get_stories(userids=[profile.userid])
        story_links = []
        for story in stories:
            for item in story.get_items():
                story_links.append(f'https://www.instagram.com/stories/{username}/{item.mediaid}')
        L.close()
        return story_links
    except:
        logging.error(f"Error fetching stories for {username}")

def create_essential_folders():
    logging.info('Checking for essential files and folders')
    folders = ['Photos', 'internal', 'sessions', 'data']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    files = {
        'data/names.csv': 'firstname,lastname,gender\n',
        'data/gmail.csv': 'email,password\n',
        'data/share_usernames.csv': '',
        'internal/setup.csv': 'emails\n',
        'data/comments.json': json.dumps({"comments": []})
    }

    for file_path, content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)

    logging.info('Essential files and folders checked successfully')

if __name__ == '__main__':
    st = get_stories('maisamayhoon')
    print(st)
