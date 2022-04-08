from asyncio.windows_events import NULL
import pandas as pd
from openpyxl import load_workbook
from selenium import webdriver
import time


driver = webdriver.Chrome()
driver.get("https://www.woot.com/alldeals?ref=w_ngh_et_1")
time.sleep(3)

for a in driver.find_elements_by_css_selector('a'):
    #href = a.get_attribute('href')
    href = a.find_element_by_partial_link_text('https://sellout.woot.com/offers/')
    if 'woot.com/offers/' in href:
            href_list = []
            href_list.append(href)

print(href_list)
        
#exit()


