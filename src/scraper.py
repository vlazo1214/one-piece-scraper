from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

import os
import time
import sys
import requests

BUFFER_TIME = 7
DEBUG = True

download_directory = "images"

if not os.path.isdir(download_directory):
    os.makedirs(download_directory, exist_ok=True)

base_url = "https://tcbonepiecechapters.com"
chapters_page = f"{base_url}/mangas/5/one-piece"

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
    if DEBUG: print("getting chapters page...")
    driver.get(chapters_page)
    time.sleep(BUFFER_TIME+3)

    if DEBUG: print("getting soup...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    counter = 0
    chapter_links = []

    if DEBUG: print("getting desired chapters...")
    for a in soup.find_all('a', href=True):
        if '/chapters/' in a['href'] and counter < num_chapters:
            chapter_links.append(a['href'])
            counter += 1
    
    if DEBUG:
        print("found chapters: ")
        for link in chapter_links:
            print(link)
        print("-"*50)

    if DEBUG: print("getting pictures of pages...")
    for link in chapter_links:
        try:
            driver.get(base_url + link)
            chapter = link.split('/')[-1].split('-')[-1]
            if DEBUG: print(f"Processing Chapter {chapter}...")
            time.sleep(BUFFER_TIME+3)

            curr_soup = BeautifulSoup(driver.page_source, 'html.parser')

            all_imgs = curr_soup.find_all('img', attrs={'class': 'fixed-ratio-content'})
            for i, img in enumerate(all_imgs):
                if DEBUG: print(f"Processing page {i+1}/{len(all_imgs)}...")
                filename = f"{chapter}-{i+1}.png"
                filepath = os.path.join(download_directory, filename)

                response = requests.get(img.attrs['src'], timeout=5)

                if response.status_code == 200:
                    with open(filepath, 'wb') as file:
                        file.write(response.content)
                else:
                    print(f"Failed to download chapter {chapter} page {i+1}")


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
