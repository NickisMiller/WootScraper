import time
import re
import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Set true to compare to amazon.com prices
search_amazon = False

# Set 'False' for all pages, or set number of pages you want + 1
top_woot_items = 2

woot_url = "https://www.woot.com/alldeals?ref=w_ngh_et_1"

# Export file name
file_name_save = "export_woot_bot_{}.csv".format(
    int(round(datetime.now().timestamp())))

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(woot_url)

# xpath vars here for easy chaning
final_page_xpath = "/html/body/div[2]/div/div/div/div[3]/div/div[6]/div/div"
item_name_xpath = "/html/body/div[2]/section[1]/section[1]/article[1]/div[3]/header/h1"
item_name_xpath_2 = "/html/body/div[2]/section[1]/section[1]/article[1]/div[4]/header/h1"

# God I hate xpath - it's the only way...
# Searches for the xpath until it finds it, will add some failsafe later
while True:
    try:
        final_page_number = int(
            driver.find_element_by_xpath(final_page_xpath).text) + 1
        break
    except NoSuchElementException:
        time.sleep(.1)

href_library = []
woot_item_values = {}


def Scrape_Page(page_number):
    global href_library
    IterateCounter = 0

    # Get request for page number in the main woot_url
    if(page_number != 1):
        woot_url_page_id = (woot_url + "&page={}".format(str(page_number)))
        driver.get(woot_url_page_id)
        time.sleep(1)

    while True:
        try:
            # Find how many elements are on first page and place links into list
            div_locator_href = "div[data-test-ui='offerItem{}']".format(
                str(IterateCounter))

            dom_item = (driver.find_element_by_css_selector(
                div_locator_href).find_elements_by_css_selector("a"))

            for a in dom_item:
                href_library.append(a.get_attribute("href"))

            IterateCounter += 1
        except NoSuchElementException:
            break


def Get_Product_Info(href, link_progress):
    global woot_item_values

    driver.get(href)
    html_source = driver.page_source

    # Get the following informaion from woot
    try:
        item_asin = html_source.split("Asin\":\"")[1].split("\"")[0]
    except IndexError:
        item_asin = 'null'

    try:
        item_price = driver.find_elements_by_class_name("price")[0].text
        item_price = float(item_price.replace(",", "").split("$")[-1])
    except:
        # Possibly from the range of prices where you select from different options
        item_price = "null - unknown error"

    try:
        item_name = driver.find_element_by_xpath(item_name_xpath).text
    except NoSuchElementException:
        try:
            # If there is a sale, it moves to a different xpath?
            # We should find a better way to solve this issue
            item_name = driver.find_element_by_xpath(item_name_xpath_2).text
        except NoSuchElementException:
            item_name = "null"

    # Put into a dictionary for pushing to csv file
    woot_item_values[item_asin] = {
        "ASIN": item_asin,
        "Price": item_price,
        "Name": item_name,
        "URL": href
    }

    # Save to temp csv file as its running - saves every 50 items
    if(link_progress % 50 == 0):
        with open("temp-file.csv", 'w') as f:
            write_head_once = True
            for asin, values in woot_item_values.items():
                w = csv.DictWriter(f, values.keys())
                if write_head_once:
                    w.writeheader()
                write_head_once = False
                w.writerow(values)


if (top_woot_items >= final_page_number) or (top_woot_items == False):
    set_page_range = final_page_number
else:
    set_page_range = top_woot_items

# Start at index of 1, loop until page end or what is specified above
for page in range(1, set_page_range):
    Scrape_Page(page)

# CLI updates for how many links have been processed so far
# Good for debugging
total_links_processed = 0
for href in href_library:
    Get_Product_Info(href, total_links_processed)
    total_links_processed += 1
    print(str(total_links_processed) + ": " + href)

# Please god chrome, stop using all my ram
driver.quit()

# Write the dictionary to the CSV file
with open(file_name_save, 'w') as f:
    write_head_once = True
    for asin, values in woot_item_values.items():
        w = csv.DictWriter(f, values.keys())
        if write_head_once:
            w.writeheader()
        write_head_once = False
        w.writerow(values)
