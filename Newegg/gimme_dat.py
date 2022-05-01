import time
import re
import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
#from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime


driver = webdriver.Chrome()
driver.get("https://www.newegg.com/")

todays_deals = driver.find_element_by_xpath("//*[@id='trendingBanner_677316']/span")
time.sleep(1)
todays_deals.click()
