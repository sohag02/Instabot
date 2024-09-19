import json
import random
import time
from multiprocessing import Pool
from typing import Dict, List, Optional, Tuple

from actions import comment, follow, like, watch_story, share, work_on_story
from config import Config
from driver import setup_driver
from utils import get_proxies
from proxy_extension import create_proxy_auth_extension
from utils import wait_for_page_load
import logging
import csv

logger = logging.getLogger(__name__)


def process_batch(func, accounts_batch, config: Config, count_list: List[int], story_links: List[str], size: int = 5) -> List[Tuple[int, int, int, int]]:
    with Pool(size) as pool:
        if config.use_proxy:
            if config.rotating_proxies:
                proxy = create_proxy_auth_extension(
                    config.host, config.port, config.proxy_username, config.proxy_password, "internal")
                proxies_batch = [proxy for _ in range(len(accounts_batch))]
            else:
                proxies = get_proxies()
                proxies_batch = [proxies.pop(0).strip()
                                 for _ in range(len(accounts_batch))]
        else:
            proxies_batch = [None for _ in range(len(accounts_batch))]

        args = [(cred, links, proxy, account_map, config, count_list, story_links) for (cred, links, account_map), proxy in zip(accounts_batch, proxies_batch)]
        return pool.starmap(func, args)


def process_reels(credential: str, links: List, proxy: Optional[str], account_map: Dict[str, List[str]], config: Config, count_list: List[int], story_links: List[str]) -> Tuple[int, int, int, int]:
    likes_count, comments_count, shares_count, follow_count = count_list
    driver = setup_driver(credential, headless=config.headless)
    driver.get(f'https://www.instagram.com/{config.target_username}/reels/')
    wait_for_page_load(driver)
    time.sleep(2)

    if config.follows and follow_count < config.follows:
        res = follow(driver)
        if res:
            follow_count += 1

    if config.content.story and story_links:
        # watch_story(driver, config.target_username)
        work_on_story(driver, story_links)

    if config.comments:
        with open('data/comments.json') as f:
            comments = json.load(f)['comments']

    if config.shares:
        with open('data/share_usernames.csv') as f:
            coulumn = csv.reader(f)
            share_usernames = [row[0] for row in coulumn]

    if not links:
        return

    for link in links:
        driver.get(link)
        wait_for_page_load(driver)
        time.sleep(2)
        if credential not in account_map.get(link, []):
            continue

        if likes_count < (config.likes or 0):
            if like(driver):
                likes_count += 1

        if comments_count < (config.comments or 0):
            com = random.choice(comments)
            if comment(driver, com):
                comments_count += 1

        if shares_count < (config.shares or 0):
            users_to_share = random.sample(share_usernames, config.shares)
            share(driver, users_to_share)

        if config.watch_time:
            time.sleep(config.watch_time)

    driver.quit()
    return likes_count, comments_count, shares_count, follow_count
