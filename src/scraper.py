from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import time


options = Options()
# options.profile = "/home/viviteto/snap/firefox/common/.mozilla/firefox/wt0sip99.seleniumprofile"

driver = webdriver.Firefox(options=options)

driver.get("http://www.google.com")
assert "Google" in driver.title
search_box = driver.find_element("name", "q")
search_box.send_keys("Selenium Python")
search_box.send_keys(Keys.RETURN)
time.sleep(5) # Give time for results to load
print(driver.title)
driver.quit()
