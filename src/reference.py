from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import time
import json

# could change as needed
BUFFER_TIME = 7

options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# get webdriver
driver = uc.Chrome(options=options)

try:
    # read base site
    site_url = "https://wdwpassport.com/past-crowds"
    driver.get(site_url)
    time.sleep(BUFFER_TIME)  # Wait for page to load
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # get all hrefs of June 2024 to June 2025 data
    crowd_hrefs = []
    months_24 = ["june", "july", "august", "september", "october", "november", "december"]
    months_25 = ["january", "february", "march", "april", "may", "june"]

    for a in soup.find_all('a', href=True):
        if (a['href'].split('-')[-1] == '2024' and a['href'].split('/')[-1].split('-')[-2] in months_24) or (a['href'].split('-')[-1] == '2025' and a['href'].split('/')[-1].split('-')[-2] in months_25):
            crowd_hrefs.append(a['href'])
            break

    print(f"Found {len(crowd_hrefs)} links for June 2024 to June 2025")

    month_to_days = {}

    # iterate over all 13 hrefs and build wait times from each park
    for i, link in enumerate(crowd_hrefs):
        try:
            print(f"\nProcessing {i+1}/{len(crowd_hrefs)}: {link}")
            driver.get(link)

            curr_month = link.split('/')[-1]
            month_to_days[curr_month] = []

            time.sleep(BUFFER_TIME + 3)  # Wait for page to load and avoid rate limiting
            
            curr_soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            all_refs = curr_soup.find_all('a', href=True)

            for j, a in enumerate(all_refs):
                if '/'.join(a['href'].split('/')[:-1]) == link:
                    month_to_days[curr_month].append(a['href'])
                    break
            
        except Exception as e:
            print(f"Error processing {link}: {e}")
    
    for i, month in enumerate(month_to_days.keys()):
        curr_month = month_to_days[month]

        for j, day_link in enumerate(curr_month):
            driver.get(day_link)

            time.sleep(BUFFER_TIME)

            curr_soup = BeautifulSoup(driver.page_source, 'html.parser')

            # search for h3 tags to get rides
            for content in curr_soup.find_all('div', attrs={'x-show':'currentTab == \'mk\' || currentTab == \'all\'' or 'currentTab == \'ak\' || currentTab == \'all\'' or 'currentTab == \'ep\' || currentTab == \'all\'' or 'currentTab == \'hs\' || currentTab == \'all\''}):
                print(content)

            # avg wait times?

            exit()

finally:
    driver.quit()

# write to csv