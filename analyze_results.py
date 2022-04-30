# https://www.profitguru.com/calculator/fba
# https://sellercentral.amazon.com/revcal?ref=RC1

import time
import csv
from itertools import zip_longest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime

# CSV file to read locally
main_csv_file = "export_woot_bot_1651300916.csv"

# Export file name
file_name_save = "export_analyze_results_{}.csv".format(
    int(round(datetime.now().timestamp())))

# More fucking xpath vars... boooo....
calculate_button_xpath = "/html/body/main/div/div[3]/div[1]/div[2]/form/div[2]/div[1]/button"
net_profit_xpath = "/html/body/main/div/div[3]/div[1]/div[2]/form/div[1]/div[1]/div/div/div/table/tbody/tr[7]/td[1]/span"
roi_xpath = "/html/body/main/div/div[3]/div[1]/div[2]/form/div[1]/div[1]/div/div/div/table/tbody/tr[9]/td[1]/span"
amazon_price_xpath = "/html/body/main/div/div[3]/div[1]/div[2]/div/div[2]/div/div/div/table/tbody/tr[1]/td[2]/div[1]/span[2]"

# get to asin site
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.profitguru.com/calculator/fba")

# Initilize vars
asin_csv = []
price_csv = []

net_profit = []
roi = []
amazon_price = []

# Read csv file and pull ASIN number
with open(main_csv_file, "r", newline="") as file:
    reader = csv.reader(file, delimiter=",")
    for row in reader:
        # Skips the title row and puts the rest into lists
        if row[0] != "ASIN":
            asin_csv.append(row[0])
        if row[1] != "Price":
            price_csv.append(row[1])

asin_input = driver.find_element_by_id("load_asin_asin")
cost_price_input = driver.find_element_by_id("fba_calculation_supplierPrice")
search_button = driver.find_element_by_id("search-button")

for asin, price in zip(asin_csv, price_csv):
    asin_input.clear()
    asin_input.send_keys(asin)
    search_button.click()

    cost_price_input.clear()
    cost_price_input.send_keys(price)

    calculate_button = driver.find_element_by_xpath(calculate_button_xpath)
    calculate_button.click()

    # Looks for the amazon link (amazon.com/dp/ASIN#) and continues once it's found
    while True:
        html_source = driver.page_source
        if html_source.find("/dp/" + asin) != -1:
            break
        else:
            time.sleep(.1)

    # Collect information from website
    net_profit.append(driver.find_element_by_xpath(net_profit_xpath).text)
    roi.append(driver.find_element_by_xpath(roi_xpath).text)
    amazon_price.append(driver.find_element_by_xpath(amazon_price_xpath).text)

# Write the items to CSV file - idk I just copied this code from stackoverflow and it works
d = [asin_csv, price_csv, net_profit, roi, amazon_price]
export_data = zip_longest(*d, fillvalue='')
with open(file_name_save, 'w', encoding="ISO-8859-1", newline='') as f:
    wr = csv.writer(f)
    wr.writerow(("ASIN", "Woot Price", "Net Profit", "ROI", "Amazon Price"))
    wr.writerows(export_data)
f.close()

########### TODO ###############
# READ CSV ----- DONE
# INPUT ASIN AND PRICE INTO CALCULATOR ---- DONE
# GRAB IMPORTANT INFO FROM CALCULATOR (PROFIT, ROI, AMAZON PRICE)
