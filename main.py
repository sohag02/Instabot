import random
import logging
from config import Config
from livestream import livestream
from process import process_batch, process_reels
from utils import get_links
from driver import setup_driver
import os
# from Scapper.scrape_followers import Scrapper, get_sessionid
from utils import get_accounts
from proxy import check_proxies
from monitor import monitor_content
from typing import List, Dict
import multiprocessing
from utils import get_stories, create_essential_folders
# from counter import Counter

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s- %(filename)s - %(levelname)s - %(message)s')
logging.getLogger('instagrapi').setLevel(logging.ERROR)


def load_accounts(config: Config) -> List[str]:
    accounts = os.listdir('sessions')
    accounts = list(map(lambda acc: acc.replace('.zip', ''), accounts))
    # Use 1 as default if config.accounts is None
    return random.sample(accounts, config.accounts or 1)


def assign_accounts(links: List[str], max_action: int, accounts: List[str]) -> Dict[str, List[str]]:
    return {
        link: random.sample(accounts, max_action) for link in links
    }


def main(config: Config):
    if config.use_proxy and not config.rotating_proxies:
        check_proxies(config.proxy_file)

    accounts = get_accounts(config.accounts or 1)
    if not accounts:
        exit()
    for account in accounts:
        driver = setup_driver(account.replace('.pkl', ''))
        if driver:
            break
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
        config.likes/config.range,
        config.comments/config.range,
        config.follows
    )
    print(max_action, 'max_action')
    if max_action > len(accounts):
        logging.error(f"Not enough accounts to perform {
                      max_action} actions. Please reduce the range.")
        exit()

    logging.info(f"Assigning random accounts to {len(links)} links")
    account_map = assign_accounts(links, int(max_action), accounts)
    print(account_map)

    if config.content.story:
        stories = get_stories(config.target_username)

    total_likes, total_comments, total_shares, total_follows = 0, 0, 0, 0
    # counter = Counter()
    for i in range(0, len(accounts), config.threads or 1):
        logging.info(f"Processing batch {i} to {i + (config.threads or 1)}")
        creds = accounts[i:i + (config.threads or 1)]
        args = [(cred, links, account_map) for cred in creds]

        batch_likes, batch_comments, batch_shares, batch_follows = process_batch(
            func=process_reels,
            accounts_batch=args,
            config=config,
            count_list=[total_likes, total_comments,
                        total_shares, total_follows],
            story_links=stories if config.content.story else [],
            size=config.threads or 1
        )
        total_likes += batch_likes
        total_comments += batch_comments
        total_shares += batch_shares
        total_follows += batch_follows

    logging.info(f"Total actions: Likes: {total_likes}, Comments: {
                 total_comments}, Shares: {total_shares}, Follows: {total_follows}")
    # logging.info(f"Total actions: Likes: {counter.get('likes')}, Comments: {counter.get('comments')}, Shares: {counter.get('shares')}, Follows: {counter.get('follows')}")


if __name__ == '__main__':
    create_essential_folders()
    config = Config()

    if config.monitor_mode:
        multiprocessing.freeze_support()
        monitor_content(config.target_username, config)
        exit()

    if config.livestream_mode:
        livestream(config)
        exit()

    main(config)
