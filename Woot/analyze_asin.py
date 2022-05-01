# Import required modules
import configparser
import time
import os
import csv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime

# Import Amazon credneitals into local dictionary
config = configparser.RawConfigParser()
config.read("/Users/codyheiser/Documents/AmazonSeller/Bots/creds.cfg")

amazon_credentials = dict(config.items("Amazon_Credentials"))

user_email = amazon_credentials["amazon_user"]
user_pass = amazon_credentials["amazon_pass"]

# CSV asin file and website url
#main_csv_file = r"./exports/export_woot_bot_1651438146.csv"

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "exports/export_woot_bot_1651438146.csv"
main_csv_file = os.path.join(script_dir, rel_path)

asin_csv = []
price_csv = []

amazon_url = "https://sellercentral.amazon.com/revcal?ref=RC1&"

# Amazon selenium directs
user_email_id = "ap_email"
user_pass_id = "ap_password"
signin_submit_id = "signInSubmit"
remember_me_name = "rememberMe"

select_storefront_class = "picker-name"
submit_storefront_class = "picker-switch-accounts-button"

asin_id = "katal-id-3"
submit_asin_xpath = "/html/body/div/div[2]/div/kat-box/div/div[1]/form/kat-button//button"

cost_goods_id = "katal-id-30"
misc_cost_goods_id = "katal-id-31"

# Amazon collect information directs
sales_rank_xpath = "/html/body/div/div[2]/div/kat-box/div/div[1]/div[3]/table/tbody/tr[3]/td[2]"
offers_xpath = "/html/body/div/div[2]/div/kat-box/div/div[1]/div[3]/table/tbody/tr[4]/td[2]"
total_reviews_xpath = "/html/body/div/div[2]/div/kat-box/div/div[1]/div[3]/table/tbody/tr[5]/td[2]/span/span"
rating_custom_dom = "kat-star-rating"

cpu_xpath = "/html/body/div/div[2]/div/div[2]/kat-box[1]/div[2]/div[2]/div/div[1]/div[1]/kat-label[2]//label/slot/span"
net_unit_profit_xpath = "/html/body/div/div[2]/div/div[2]/kat-box[1]/div[2]/div[2]/div/div[1]/div[2]/kat-label[2]//label/slot/span"
amazon_fees_xpath = "/html/body/div/div[2]/div/div[2]/kat-box[1]/div[2]/div[1]/div[3]/div/kat-expander[1]/div[1]/kat-label//label/slot/span"


def Pull_ASIN(csv_file=main_csv_file):
    global asin_csv, price_csv

    with open(main_csv_file, "r", newline="") as file:
        reader = csv.reader(file, delimiter=",")
        for row in reader:
            # Skips the title row and puts the rest into lists
            if row[0] != "ASIN":
                asin_csv.append(row[0])
            if row[1] != "Price":
                price_csv.append(row[1])


def Get_Amazon_Info(asin_list, price_list):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(amazon_url)

    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: driver.current_url != amazon_url)

    user_email_input = driver.find_element_by_id(user_email_id)
    user_pass_input = driver.find_element_by_id(user_pass_id)
    singin_submit_button = driver.find_element_by_id(signin_submit_id)
    remember_me_button = driver.find_elements_by_name(remember_me_name)[0]

    user_email_input.clear()
    user_pass_input.clear()

    user_email_input.send_keys(user_email)
    user_pass_input.send_keys(user_pass)
    remember_me_button.click()
    singin_submit_button.click()

    # Wait for OTP to be entered
    while True:
        breaker = False

        # URL changes to include /authorization/ after login
        if "authorization" in driver.current_url:
            # Select the US storefront from the list of storefronts available
            select_storefront_list = driver.find_elements_by_class_name(
                select_storefront_class)

            # Find storefront that is US - select and click continue button
            for store in select_storefront_list:
                if store.text == "United States":
                    store.click()

                    select_storefront_button = driver.find_element_by_class_name(
                        submit_storefront_class)
                    select_storefront_button.click()

                    breaker = True
                    break
                else:
                    time.sleep(.1)
        else:
            time.sleep(.1)

        if breaker:
            break

    # Redirect to original url to make sure we're on the right page
    driver.get(amazon_url)

    for asin, woot_price in zip(asin_list, price_list):
        if asin != "null":
            # Wait for data load
            time.sleep(5)
            asin_textbox = driver.find_element_by_id(asin_id)
            submit_asin_button = driver.find_element_by_xpath(
                submit_asin_xpath)

            while True:
                try:
                    asin_textbox = driver.find_element_by_id(asin_id)
                    submit_asin_button = driver.find_element_by_xpath(
                        submit_asin_xpath)
                    break
                except NoSuchElementException:
                    time.sleep(.1)

            asin_textbox.clear()

            asin_textbox.send_keys(asin)
            submit_asin_button.click()

            # Wait for data load
            while True:
                try:
                    cog_textbox = driver.find_element_by_id(cost_goods_id)
                    misc_cog_textbox = driver.find_element_by_id(
                        misc_cost_goods_id)
                    break
                except NoSuchElementException:
                    time.sleep(.1)

            cog_textbox.clear()
            misc_cog_textbox.clear()

            cog_textbox.send_keys(woot_price)
            misc_cog_textbox.send_keys()

            # Collect the Amazon info
            sales_rank = driver.find_element_by_xpath(sales_rank_xpath).text
            offers = driver.find_element_by_xpath(offers_xpath).text
            total_reviews = driver.find_element_by_xpath(
                total_reviews_xpath).text

            rating = driver.find_element_by_css_selector(
                rating_custom_dom).get_attribute("value")
            print(rating)

            cpu = driver.find_element_by_xpath(cpu_xpath).text
            net_unit_profit = driver.find_element_by_xpath(
                net_unit_profit_xpath).text
            amazon_fees = driver.find_element_by_xpath(amazon_fees_xpath).text


Pull_ASIN()
Get_Amazon_Info(asin_csv, price_csv)
