import time
import re
import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

target_url = "https://www.target.com/c/clearance/-/N-5q0ga"

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(target_url)


time.sleep(5)
clerance_items = driver.find_element_by_class_name("ebNJlV")
time.sleep(1)


