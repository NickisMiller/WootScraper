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
file_name_save = "export_woot_bot_{}.csv".format(
    int(round(datetime.now().timestamp())))

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(woot_url)

# xpath vars here for easy chaning
final_page_xpath = "/html/body/div[2]/div/div/div/div[3]/div/div[6]/div/div"
item_name_xpath = "/html/body/div[2]/section[1]/section[1]/article[1]/div[3]/header/h1"
item_name_xpath_2 = "/html/body/div[2]/section[1]/section[1]/article[1]/div[4]/header/h1"
amazon_rank_xpath = "/html/body/div[1]/div[2]/div[8]/div[23]/div/ul[1]/li/span/text()[1]"
amazon_rank_xpath_2 = "/html/body/div[1]/div[3]/div[10]/div[19]/div[7]/div/div/div/div[1]/div/div/table/tbody/tr[6]/td/span/span[1]"

# God I hate xpath - it's the only way...
while True:
    try:
        final_page_number = int(
            driver.find_element_by_xpath(final_page_xpath).text) + 1
        break
    except NoSuchElementException:
        time.sleep(.1)

href_library = []
woot_item_values = {}
amazon_item_values = {}

final_export_values = {}


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


def Search_Amazon_Prices(asin, woot_price, woot_name, woot_href):
    global amazon_item_values, amazon_rank_xpath, amazon_rank_xpath_2

    amazon_url = "https://www.amazon.com/dp/{}".format(asin)

    driver.get(amazon_url)
    html_source = driver.page_source

    try:
        price = float(
            re.sub("[^0-9^.]", "", html_source.split('displayPrice":"$')[1].split(",")[0]))
    except IndexError:
        price = "null"

    try:
        number_of_reviews = int(driver.find_elements_by_id(
            "acrCustomerReviewText")[0].text.split(" ")[0].replace(",", ""))
    except IndexError:
        number_of_reviews = "null"

    try:
        review_rating = float(driver.find_elements_by_css_selector(
            "span[data-hook='rating-out-of-text']")[0].text.split(" ")[0])
    except IndexError:
        review_rating = "null"

    try:
        rank = int(html_source.split("Best Sellers Rank")[1].split(
            " (<")[0].split("#")[1].split(" ")[0].replace(",", ""))
        category = html_source.split("Best Sellers Rank")[1].split(
            " (<")[0].split(" in ")[1].split(" (")[0]
    except IndexError:
        rank = "null"
        category = "null"

    try:
        sold_by = int(html_source.split(
            "New (")[1].split(")")[0].replace(",", ""))
    except IndexError:
        sold_by = 'null'

    amazon_item_values[asin] = {
        "ASIN": asin,
        "amazon_price": price,
        "amazon_reviews": number_of_reviews,
        "amazon_rating": review_rating,
        "amazon_rank": rank,
        "amazon_category": category,
        "amazon_url": amazon_url,
        "woot_price": woot_price,
        "woot_name": woot_name,
        "woot_url": woot_href
    }


def Get_Product_Info(href, link_progress):
    global woot_item_values, item_name_xpath

    driver.get(href)
    html_source = driver.page_source

    try:
        item_asin = html_source.split("Asin\":\"")[1].split("\"")[0]
    except IndexError:
        item_asin = 'null'

    try:
        item_price = driver.find_elements_by_class_name("price")[0].text
        item_price = float(item_price.replace(",", "").split("$")[-1])
    except:
        item_price = "null - unknown error"

    try:
        item_name = driver.find_element_by_xpath(item_name_xpath).text
    except NoSuchElementException:
        try:
            item_name = driver.find_element_by_xpath(item_name_xpath_2).text
        except NoSuchElementException:
            item_name = "null"

    if search_amazon:
        Search_Amazon_Prices(item_asin, item_price, item_name, href)

    woot_item_values[item_asin] = {
        "ASIN": item_asin,
        "Price": item_price,
        "Name": item_name,
        "URL": href
    }

    # Save to excel file as its running

    if search_amazon:
        if(link_progress % 50 == 0):
            with open("temp-file.csv", 'w') as f:
                write_head_once = True
                for asin, values in amazon_item_values.items():
                    w = csv.DictWriter(f, values.keys())
                    if write_head_once:
                        w.writeheader()
                    write_head_once = False
                    w.writerow(values)
    else:
        if(link_progress % 50 == 0):
            with open("temp-file.csv", 'w') as f:
                write_head_once = True
                for asin, values in woot_item_values.items():
                    w = csv.DictWriter(f, values.keys())
                    if write_head_once:
                        w.writeheader()
                    write_head_once = False
                    w.writerow(values)

# Search_Amazon_Prices("B099P9G7Q5")


# Final page number here - final_page_number
if (top_woot_items >= final_page_number) or (top_woot_items == False):
    set_page_range = final_page_number
else:
    set_page_range = top_woot_items

for page in range(1, set_page_range):
    Scrape_Page(page)

total_links_processed = 0
for href in href_library:
    Get_Product_Info(href, total_links_processed)
    total_links_processed += 1
    print(str(total_links_processed) + ": " + href)

driver.quit()

if search_amazon:
    with open(file_name_save, 'w') as f:
        write_head_once = True
        for asin, values in amazon_item_values.items():
            w = csv.DictWriter(f, values.keys())
            if write_head_once:
                w.writeheader()
            write_head_once = False
            w.writerow(values)
else:
    with open(file_name_save, 'w') as f:
        write_head_once = True
        for asin, values in woot_item_values.items():
            w = csv.DictWriter(f, values.keys())
            if write_head_once:
                w.writeheader()
            write_head_once = False
            w.writerow(values)
