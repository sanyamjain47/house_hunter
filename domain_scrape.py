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
from bs4 import BeautifulSoup

suburbs = parameters.suburbs
bedrooms = parameters.bedrooms
price_range = parameters.price_range
keywords = parameters.keywords
driver = load_chromedriver()
actions = ActionChains(driver)
all_houses = []

for suburb in suburbs:
    URL = generate_url("www.domain.com.au", [suburb], bedrooms, price_range, keywords=keywords)



    page_number = 1
    new_url = append_page_to_url(URL,page_number)
    all_urls = []
    while True:
        driver.get(new_url)
        XPATH_RESULT = "/html/body/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[2]/ul"
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

    for i in set_urls:
        try:
            driver.get(i)
            html_content = driver.find_element(By.CLASS_NAME,"css-2anoks")
            html_content = html_content.get_attribute('outerHTML')

            # Create a BeautifulSoup object
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extracting the price
            price = soup.find('div', {'data-testid': 'listing-details__summary-title'}).text.strip()

            # Extracting the address
            address = soup.find('h1', class_='css-164r41r').text.strip()

            # Extracting beds, bathrooms, and parking
            features = soup.find_all('span', class_='css-1ie6g1l')
            beds = bathrooms = parking = None
            for feature in features:
                text = feature.get_text()
                if 'Beds' in text:
                    beds = text.split(' ')[0]
                elif 'Bath' in text:
                    bathrooms = text.split(' ')[0]
                elif 'Parking' in text:
                    parking = text.split(' ')[0]

            all_houses.append({
                'price':price,
                'address':address,
                'beds':beds,
                'baths':bathrooms,
                'parking':parking,
                'suburb':suburb,
                'postcode':suburb[1]
            })
            
        except:
            print(i)

df = pd.DataFrame(all_houses)
df = df.drop_duplicates()
# Save the DataFrame to a CSV file
filename = 'houses.csv'
df.to_csv(filename, index=False)
print(f'Data saved to {filename}')
