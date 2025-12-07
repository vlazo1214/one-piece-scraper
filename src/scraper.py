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

if len(sys.argv) < 1:
    print("enter ff or chrome and then starting chapter")
    exit()

starting_chapter = sys.argv[2]

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
    time.sleep(BUFFER_TIME)

    if DEBUG: print("getting soup...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    for a in soup.find_all('a', href=True):
        if (a['href'].split('/')[0] == 'chapters'):
            print(a['href'])

except Exception as e:
    print(e)
    print("Exiting...")

finally:
    driver.quit()
