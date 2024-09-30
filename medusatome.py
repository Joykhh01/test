#!/usr/bin/env python
# coding: utf-8

# run on bash
# sudo apt update
# sudo apt install tor firefox-geckodriver firefox python3-pandas python3-bs4 python3-selenium
# 

# In[ ]:


import os
import pandas as pd
import numpy as np
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


# In[ ]:


# Start Tor
torexe = os.popen('tor')


# In[ ]:


# Firefox Binary and GeckoDriver Paths for Ubuntu
firefoxBinary = "/usr/bin/firefox"
geckodriverPath = "/usr/bin/geckodriver"
proxyIP = "127.0.0.1"
proxyPort = 9150

# Configure Firefox profile for Tor
profile = FirefoxProfile("/path/to/your/tor/profile")  # Replace with the correct path to your Tor profile on Ubuntu

profile.set_preference('extensions.torlauncher.start_tor', True)
profile.set_preference('network.proxy.type', 1)
profile.set_preference('network.proxy.socks', proxyIP)
profile.set_preference('network.proxy.socks_port', proxyPort)
profile.set_preference("network.proxy.socks_remote_dns", True)
profile.update_preferences()

# Launch Firefox with GeckoDriver and the configured profile
driver = webdriver.Firefox(executable_path=geckodriverPath,
                           firefox_binary=firefoxBinary, 
                           firefox_profile=profile)

# Wait until Tor connects to the network
driver.get('http://medusaxko7jxtrojdkxo66j7ck4q5tgktf7uqsqyfry4ebnxlcbkccyd.onion/')
SCROLL_PAUSE_TIME = 5

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

companyNames = []
companyDescription = []
dateVictimised = []
noClicks = []

cards = driver.find_elements_by_xpath("//div[@class='card']")

for card in cards:
    dateVictimisedElement = card.find_element_by_xpath(".//div[@class='date-updated']/span[@class='text-muted']")
    dateVictimisedText = dateVictimisedElement.text
    dateVictimised.append(dateVictimisedText)

    companyNameElement = card.find_element_by_xpath(".//h3[@class='card-title']")
    companyNameText = companyNameElement.text
    companyNames.append(companyNameText)

    companyDescriptionElement = card.find_element_by_xpath(".//p[@class='card-text text-left']")
    companyDescriptionText = companyDescriptionElement.text
    companyDescription.append(companyDescriptionText)

    noClicksElement = card.find_element_by_xpath(".//div[@class='number-view']/span[@class='text-muted']")
    noClicksText = noClicksElement.text
    noClicks.append(noClicksText)

driver.quit()


# In[ ]:


df = pd.DataFrame({"Company": companyNames, "Company Description": companyDescription, "Date Victimised": dateVictimised, "Number of Clicks": noClicks})
df['Date Victimised'] = pd.to_datetime(df['Date Victimised'], format='%Y-%m-%d %H:%M:%S')

date_mask = df['Date Victimised'].dt.year < 2024
df = df[~date_mask]
df.reset_index(drop=True)
df.to_csv("Medusa_Data.csv")


# In[ ]:


# Use WebDriver Manager for Chrome (Ubuntu)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()

def location_to_country(location):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "addressdetails": 1,
        "q": location,
        "format": "jsonv2",
        "limit": 1
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if data:
        return data[0].get("address", {}).get("country", "")
    return np.nan

companyWebsite_list = []
industry_list = []
headquarter_list = []
country_list = []

wait = WebDriverWait(driver, 5)

for company in companyNames:
    try:
        driver.get('https://www.google.com')
        search = driver.find_element(By.NAME, 'q')
        search.send_keys(company + ' linkedin')
        search.send_keys(Keys.RETURN)
        linkedin_page = driver.find_element(By.TAG_NAME, 'h3')  # clicking the first search result
        time.sleep(2)
        linkedin_page.click()

        if "linkedin" in driver.current_url:
            loaded = wait.until(EC.presence_of_element_located((By.ID, "main-content")))

            try:
                website_element = driver.find_element(By.CSS_SELECTOR, '[data-test-id="about-us__website"]')
                website_text_element = website_element.find_element_by_xpath(".//dd[@class='font-sans text-md text-color-text break-words overflow-hidden']")
                website_text = website_text_element.text
            except Exception:
                website_text = np.nan
            companyWebsite_list.append(website_text)

            try:
                industry_element = driver.find_element(By.CSS_SELECTOR, '[data-test-id="about-us__industry"]')
                industry_text_element = industry_element.find_element_by_xpath(".//dd[@class='font-sans text-md text-color-text break-words overflow-hidden']")
                industry_text = industry_text_element.text
            except Exception:
                industry_text = np.nan
            industry_list.append(industry_text)

            try:
                headquarters_element = driver.find_element(By.CSS_SELECTOR, '[data-test-id="about-us__headquarters"]')
                headquarters_text_element = headquarters_element.find_element_by_xpath(".//dd[@class='font-sans text-md text-color-text break-words overflow-hidden']")
                headquarters_text = headquarters_text_element.text
                country = location_to_country(headquarters_text)
            except Exception:
                headquarters_text = np.nan
                country = np.nan
            headquarter_list.append(headquarters_text)
            country_list.append(country)
        else:
            companyWebsite_list.append(np.nan)
            industry_list.append(np.nan)
            headquarter_list.append(np.nan)
            country_list.append(np.nan)

    except Exception:
        companyWebsite_list.append(np.nan)
        industry_list.append(np.nan)
        headquarter_list.append(np.nan)
        country_list.append(np.nan)

driver.quit()


# In[ ]:


df["Company Website"] = companyWebsite_list
df["Industry"] = industry_list
df["Location"] = headquarter_list
df["Country"] = country_list


# In[ ]:


df.to_csv("Medusa_Linkedin_Data.csv")

