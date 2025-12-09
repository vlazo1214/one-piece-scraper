from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import time
import json
import re
import traceback

ONE_ITER = False

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
    months_25 = ["january", "february", "march", "april", "may"]

    for a in soup.find_all('a', href=True):
        if (a['href'].split('-')[-1] == '2024' and a['href'].split('/')[-1].split('-')[-2] in months_24) or (a['href'].split('-')[-1] == '2025' and a['href'].split('/')[-1].split('-')[-2] in months_25):
            crowd_hrefs.append(a['href'])
            if ONE_ITER:
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
                    
                    # if ONE_ITER:
                    #     break
            
        except Exception as e:
            print(f"Error processing {link}: {e}")
    
    print("\n", "-" * 50)
    print("Successfully scraped all day links")
    print("-" * 50)

    attr_to_month_wait = {}
    possible_xshows = re.compile(r"currentTab == '(mk|ak|ep|hs)' \|\| currentTab == 'all'")

    print_count = 0

    for i, month in enumerate(month_to_days.keys()):
        curr_month = month_to_days[month]

        print(f"\nProcessing {i+1}/{len(month_to_days.keys())}: {month}")

        for j, day_link in enumerate(curr_month):
            driver.get(day_link)

            print(f"\nProcessing {day_link}")

            time.sleep(BUFFER_TIME)

            curr_soup = BeautifulSoup(driver.page_source, 'html.parser')

            # search for h3 tags to get rides
            for content in curr_soup.find_all('div', attrs={'x-show': possible_xshows}):
                try:
                    info = content.text.strip().split('\n')
                    attraction = info[0]

                    if attraction not in attr_to_month_wait:
                        attr_to_month_wait[attraction] = {}
                    
                    if month not in attr_to_month_wait[attraction]:
                        attr_to_month_wait[attraction][month] = []

                    for item in info:
                        if len(item) == 0:
                            continue
                        if item.split(':')[0] == "Avg Posted Wait":
                            attr_to_month_wait[attraction][month].append([month.split('-')[0] + str(j+1), int(item.split(':')[1].strip().split(' ')[0])])
                            # if ONE_ITER:
                                # break

                except Exception as e:
                    print(e)
                    print(info)
                    continue

    for attraction in attr_to_month_wait.keys():
        try:
            months = attr_to_month_wait[attraction].keys()
            for month in months:
                curr_total = 0
                for day in attr_to_month_wait[attraction][month]:
                    curr_total += day[1]
                
                if len(attr_to_month_wait[attraction][month]) > 0:
                    attr_to_month_wait[attraction][month].append([month.split('-')[0] + '_month_avg', curr_total / len(attr_to_month_wait[attraction][month])])
        except Exception as e:
            print(e)
            traceback.print_exc()



            
    with open('attraction_to_waittime.json', 'w') as file:
        file.write(json.dumps(attr_to_month_wait))
    print("Saved to attraction_to_waittimes.json")

finally:
    driver.quit()
