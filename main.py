import random
import logging
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from config import Config
from process import process_batch, process_reels
from utils import get_links
from driver import setup_driver
import os
from Scapper.scrape_followers import Scrapper, get_sessionid
from utils import get_random_session, get_share_usernames, get_accounts
from proxy import check_proxies
from monitor import monitor, monitor_content
from typing import List, Dict, Optional
import multiprocessing
from utils import get_stories, create_essential_folders

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s- %(filename)s - %(levelname)s - %(message)s')
logging.getLogger('instagrapi').setLevel(logging.ERROR)


def load_accounts(config: Config) -> List[str]:
    accounts = os.listdir('sessions')
    accounts = list(map(lambda acc: acc.replace('.zip', ''), accounts))
    # Use 1 as default if config.accounts is None
    return random.sample(accounts, config.accounts or 1)


def assign_accounts(links: List[str], max_action: int, accounts: List[str]) -> Dict[str, List[str]]:
    account_map = {}
    for link in links:
        account_map[link] = random.sample(accounts, max_action)
    return account_map


def main(config: Config):
    if config.use_proxy and not config.rotating_proxies:
        check_proxies(config.proxy_file)

    accounts = get_accounts(config.accounts or 1)
    if not accounts:
        exit()

    driver = setup_driver(accounts[0].replace('.pkl', ''))
    links = []
    if config.content.reels:
        reels = get_links(driver, config.target_username, config.range, 'reel')
        links.extend(reels)
    if config.content.photos:
        photos = get_links(driver, config.target_username,
                           config.range, 'photo')
        links.extend(photos)
    driver.quit()

    max_action = max(
        (config.likes or 0) // (config.range or 1),
        (config.comments or 0) // (config.range or 1),
        config.follows or 0
    )
    if max_action > len(accounts):
        logging.error(f"Not enough accounts to perform {max_action} actions. Please reduce the range.")
        exit()

    account_map = assign_accounts(links, max_action, accounts)

    if config.content.story:
        stories = get_stories(config.target_username)

    total_likes, total_comments, total_shares, total_follows = 0, 0, 0, 0
    for i in range(0, len(accounts), config.threads or 1):
        logging.info(f"Processing batch {i} to {i + (config.threads or 1)}")
        creds = accounts[i:i + (config.threads or 1)]
        args = [(cred, links, account_map) for cred in creds]
        count_list = [total_likes, total_comments, total_shares, total_follows]
        results = process_batch(
            process_function=process_reels,
            args=args,
            config=config,
            count_list=count_list,
            stories=stories,
            size=config.threads or 1
        )
        batch_likes, batch_comments, batch_shares, batch_follows = map(sum, zip(*results))
        total_likes += batch_likes
        total_comments += batch_comments
        total_shares += batch_shares
        total_follows += batch_follows

    logging.info(f"Total actions: Likes: {total_likes}, Comments: {total_comments}, Shares: {total_shares}, Follows: {total_follows}")


if __name__ == '__main__':
    create_essential_folders()
    config = Config()

    if config.scrapper_mode:
        session = get_random_session()
        if not session:
            logging.error('No session found. Please run login.py first.')
            exit()
        session_id = get_sessionid(session)
        scrapper = Scrapper(sessionid=session_id)
        followers = scrapper.get_followers(config.target_username, config.range)
        with open(f'{config.target_username}.txt', 'w') as f:
            for follower in followers:
                f.write(follower + '\n')
        exit()

    if config.monitor_mode:
        multiprocessing.freeze_support()
        monitor_content(config.target_username, config)
        exit()

    main(config)
