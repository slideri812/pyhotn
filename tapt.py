#!/usr/bin/env python
# coding: utf-8

##part 1
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

##part 2
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from random import randint
from urllib.request import urlopen as uReq
from requests import get
import numpy as np


###PART 1 - GET LINKS FROM LINKS PAGE
# URL of target page
url = "https://www.thaiapartment.com/apartmentbyproject" 

# Open the URL and read the whole page
html = urllib.request.urlopen(url).read()

# Parse the string
soup = BeautifulSoup(html, "html.parser")

# Retrieve all of the anchor tags
tags = soup("a")

links = []

#Prints all the links in the list tags
for tag in tags: 
    link = "https://www.thaiapartment.com"+tag.get("href", None)
    links.append(link)

# Declare the filter function
def Filter(links):
    # Search data based on regular expression in the list
    return [val for val in links
        if re.search(r"^https://www.thaiapartment.com/apartment/", val)]

#print(Filter(links))
linkext = Filter(links)

# Panda Data Frame format output
aptlist = pd.DataFrame({
"Link": linkext,
})

#save panda frame to file
aptlist.to_csv("ThaiAptsAptList.csv", index = False)

# print("""List saved to file. 
# Links ready as linkext""")
print(len(aptlist))
print("Links Ready As linktext")


##PART2 - SCRAPES EACH LINK FOR DATA
# instantiate a chrome options object so you can set the size and headless preference
chrome_options = Options()
chrome_options.add_argument("headless")
chrome_options.add_argument("window-size=1920x1080")

#load broswer controls open window
driver = webdriver.Chrome(ChromeDriverManager().install())

#open browser in fullscreen
#driver.maximize_window()

index = 1
master_list = []
#loads the target url
for url in linkext[0:-1]:
    try:
        driver.get(url)
        print(index, url)
        index += 1
    except:
        print("timedout - failed toload page")
        continue

    #container for pg source html
    html = driver.page_source

    #envokes soup html parser
    soup = BeautifulSoup(html,"html.parser")
    
    #to deal with non 404/ unexpected site errors
    try:
        soup.find("li", {"class":"flex-active-slide"}).img.get("src")
    except:
        print("No Active Slide On Page")
        continue

    sleep(randint(2,8))
    for detail in soup:
        data_dict = {}

        #title
        try:
            df = pd.read_html(html)[0]
            table = df.loc[0]
            type = table.iat[0]
            data_dict["title"] = type + (" Apartment")
        except Exception:
            data_dict["title"] = ("Apartment")

        #subtitle
#         data_dict["subtitle"] = detail.title.text.strip()

        try:
            data_dict["subtitle"] = detail.title.text.strip()
        except:
            data_dict["subtitle"] = None

        #location
#         try: #this is wrongfully pulling info from the cards at the bottom of the page - Site had code change 
#             data_dict["location"] = detail.find("a",{"id":"myDataList_lblLocation_1"}).text.strip()[10:]
#         except AttributeError as e:
#             data_dict["location"] = None

#         try: #this was the orginal location 2
#             data_dict["location2"] = detail.find("span",{"id":"lblAddress"}).text.strip()
#         except AttributeError as e:
#             data_dict["location2"] = None

        #this is the update - fixes some problems but loops 110 times when it encounters an error
        try:
            data_dict["location"] = detail.find("span",{"id":"lblAddress"}).text.strip()
        except Exception as e1:
            print("location Exception 1")            
            print(e1)
            data_dict["location"] = ("location error 1")
        except Exception as e2:
            print("location Exception 2")
            print(e2)
            data_dict["location"] = ("location error 2")

        #rates
        try:
#             df = pd.read_html(html)[0]
#             table = df.loc[0]
            price = table.iat[-1]
            data_dict["price"] = price
        except Exception as e:
            data_dict["price"] = ("")
            print("Table not found")

        #link to listing
        data_dict["link"] = url

        #link to image        
        try:
            data_dict["image"] = soup.find("li", {"class":"flex-active-slide"}).img.get("src")
        except Exception as e:
            data_dict["image"] = ("")
            print("Image not found")

        #source
        data_dict["source"] = ("https://www.thaiapartment.com")

        #major
        patterns = ["Bangkok", "Phuket", "Chiang Mai", "Pattaya", "Chon Buri", "None"]
        text_to_search = (data_dict["location"])

        for pattern in patterns:
            if re.search(pattern, text_to_search):
                break

        if pattern == "Bangkok":
            data_dict["major locations"] = "54fbfc7f-a0cf-4a1d-9361-6059a44c2415"
        elif pattern == "Phuket":
            data_dict["major locations"] = "cbad67b4-7870-4ee2-b8a3-62d8c9f87091"
        elif pattern == "Chiang Mai":
            data_dict["major locations"] = "2966d83a-04f9-4b4e-b27e-05afe700b13f"
        elif pattern == "Pattaya":
            data_dict["major locations"] = "fbfaabca-0e9e-4db4-be1c-6cc8e8b8f63d"
        elif pattern == "Chon Buri":
            data_dict["major locations"] = "ce1da47b-78b6-4351-b849-e337db181c6a"
        else:
            data_dict["major locations"] = ("No Match Found")

        #logo
        data_dict["logo"] = ("https://static.wixstatic.com/media/299fde_ec03930ceadf4a4882ba5bb4cfd47db9~mv2.png")

        #host
        data_dict["host"] = ("Thai Apartments")
        
        #near by station            
        try:
            data_dict["station1"] = detail.find("span", {"id":"myDataList_lblStation_0"}).text.strip()
        except Exception as e:
            data_dict["station1"] = None
            
        try:
            data_dict["station2"] = detail.find("span", {"id":"myDataList_lblStation_1"}).text.strip()
        except Exception as e:
            data_dict["station2"] = None
     
        try:
            data_dict["station3"] = detail.find("span", {"id":"myDataList_lblStation_2"}).text.strip()
        except Exception as e:
            data_dict["station3"] = None

        master_list.append(data_dict)
  
driver.close()

print()
print("Finished Phase 2")
print()


##PART 3 - Dropping row missing price and or title
# Panda Data Frame format output
postlist = pd.DataFrame(master_list)

##enable for single file export
postlist.to_csv("tapt.csv", mode = "w", header=True, index=False)
postlist.to_csv("seamaster.csv", mode = "a", header=False, index=False)

##enaable for append mode - disable export above
# postlist.to_csv("ThaiList.csv", mode = "a", header = False, index = False)

print("Finished Phase 2" + "\n" + "File Exported")
