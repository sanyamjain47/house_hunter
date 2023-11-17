from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import json
import time
import numpy as np
from bs4 import BeautifulSoup
import json
import base64
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import re

SCROLL_PAUSE_TIME = 5

def extract_number(text):
    match = re.search(r'\d+', text)
    return match.group() if match else None


def append_page_to_url(url, page_number):
    # Parse the URL
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Add or update the 'page' parameter
    query_params['page'] = [page_number]

    # Reconstruct the URL with the updated query parameters
    updated_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=updated_query))

    return new_url

def generate_url(
    domain, suburbs, bedrooms, price_range, exclude_deposit_taken=True, keywords=None
):
    # Base URL
    base_url = f"https://{domain}/rent/?suburb="

    # Suburbs
    suburb_str = ",".join(f"{suburb}-nsw-{postcode}" for suburb, postcode in suburbs)

    # Bedrooms
    bedroom_str = f"bedrooms={bedrooms}"

    # Price Range
    price_str = f"price={price_range[0]}-{price_range[1]}"

    # Exclude Deposit Taken
    exclude_deposit_str = "excludedeposittaken=1" if exclude_deposit_taken else ""

    # Keywords
    if keywords and len(keywords) != 0:
        # Encoding the keywords for URL
        encoded_keywords = ",".join(keywords).replace(" ", "%20").replace(",", "%2C")
        keyword_str = f"keywords={encoded_keywords}"
    else:
        keyword_str = ""

    # Constructing the final URL
    parameters = [
        param
        for param in [
            suburb_str,
            bedroom_str,
            price_str,
            exclude_deposit_str,
            keyword_str,
        ]
        if param
    ]
    final_url = base_url + "&".join(parameters)
    print(final_url)
    return final_url


def load_chromedriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
    )
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-single-click-autofill")
    chrome_options.add_argument("--disable-autofill-keyboard-accessory-view[8]")
    chrome_options.add_argument("--disable-full-form-autofill-ios")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def autoscroller(driver):
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return driver


def fetch_response_body(driver, request_id):
    response_body = driver.execute_cdp_cmd(
        "Network.getResponseBody", {"requestId": request_id}
    )
    body = response_body.get("body")
    base64_encoded = response_body.get("base64Encoded", False)

    if base64_encoded:
        body = base64.b64decode(body).decode("utf-8")
    return body


def parse_log_entries(log_entries, driver):
    for entry in log_entries:
        try:
            process_log_entry(entry, driver)
        except Exception as e:
            continue


def process_log_entry(entry, driver):
    obj_serialized = entry.get("message")
    obj = json.loads(obj_serialized)
    message = obj.get("message")
    method = message.get("method")
    params = message.get("params")
    request_id = params.get("requestId")
    response = params.get("response")

    url = response.get("url")
    if "rent/?suburb" in url:
        process_url(driver, request_id)


def process_url(driver, request_id):
    html_content = fetch_response_body(driver, request_id)
    soup = BeautifulSoup(html_content, "lxml")
    script_tag = soup.find("script", {"type": "application/ld+json"})

    if script_tag:
        extract_and_print_json(script_tag)
    else:
        print("Script tag not found")


def extract_and_print_json(script_tag):
    json_str = script_tag.string
    try:
        data = json.loads(json_str)
        process_json(data)  # Pretty-print the JSON data
    except json.JSONDecodeError:
        print("Error decoding JSON")


def process_json(data):
    urls = []
    for i in data:
        if "location" in i and "@type" in i["location"]:
            if i["location"]["@type"] == "Residence" and "url" in i:
                urls.append(i["url"])
    print(urls)
