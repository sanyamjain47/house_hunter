from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import json
import time
import numpy as np
from helper_functions import *
import parameters

suburbs = parameters.suburbs

bedrooms = parameters.bedrooms
price_range = parameters.price_range
keywords = parameters.keywords

URL = generate_url("www.domain.com.au", suburbs, bedrooms, price_range, keywords=keywords)


driver = load_chromedriver()
actions = ActionChains(driver)

page_number = 1
new_url = append_page_to_url(URL,page_number)
all_urls = []
while True:
    driver.get(new_url)
    XPATH_RESULT = "/html/body/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/ul"
    XPATH_NEXT = "/html/body/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[3]/div[1]/div/a"
    try:
        element = driver.find_element(By.XPATH,XPATH_RESULT)
    except:
        break
    anchor_elements = element.find_elements(By.TAG_NAME, 'a')

    # Iterate over the anchor elements and extract the href attributes
    hrefs = [anchor.get_attribute('href') for anchor in anchor_elements]
    all_urls.extend(hrefs)
    # DO SOMETHING WITH HREFS
    page_number += 1
    new_url = append_page_to_url(URL, page_number)

set_urls = set(all_urls)
print(set_urls)