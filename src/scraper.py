from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

import time
import sys

BUFFER_TIME = 7
DEBUG = True

base_url = "https://tcbonepiecechapters.com/mangas/5/one-piece"

if len(sys.argv) < 2:
    print()
    print("Enter ff or chrome and then number of chapters desired starting from the most recent one.")
    print()
    exit()

num_chapters = int(sys.argv[2])

if sys.argv[1] == 'ff':
    options = Options()

    driver = webdriver.Firefox(options=options)
    if DEBUG: print("firefox as browser...")

elif sys.argv[1] == 'chrome':
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    if DEBUG: print("chrome as browser...")

try:
    if DEBUG: print("getting base url...")
    driver.get(base_url)
    time.sleep(BUFFER_TIME+3)

    if DEBUG: print("getting soup...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    counter = 0
    chapter_links = []

    if DEBUG: print("getting desired chapters...")
    for a in soup.find_all('a', href=True):
        if '/chapters/' in a['href'] and counter < num_chapters + 1:
            chapter_links.append(a['href'])
            counter += 1
    
    if DEBUG: print("getting pictures of pages...")
    for link in chapter_links:
        try:
            driver.get(link)
            time.sleep(BUFFER_TIME+3)
            break

        except Exception as e:
            print(e)


finally:
    try:
        driver.quit()
    except Exception as e:
        if "The handle is invalid" in str(e):
            print("Warning: Browser handle invalid, ignoring...")
        else:
            raise e  # Re-raise if it's a different error
    print("Exiting...")
