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

asin_cstm = "[unique-id='katal-id-3']"
submit_asin_cstm = "kat-button[label='Search']"

cost_goods_cstm = "[unique-id='katal-id-30']"
misc_cost_goods_cstm = "[unique-id='katal-id-31']"

# Amazon collect information directs
cpu_xpath = "kat-label[text='Estimated cost per unit']"
net_unit_profit_xpath = "/html/body/div/div[2]/div/div[2]/kat-box[1]/div[2]/div[2]/div/div[1]/div[2]/kat-label[2]//label/slot/span"
amazon_fees_xpath = "/html/body/div/div[2]/div/div[2]/kat-box[1]/div[2]/div[1]/div[3]/div/kat-expander[1]/div[1]/kat-label//label/slot/span"


def Pull_ASIN(csv_file=main_csv_file):
    global asin_csv, price_csv

    with open(main_csv_file, "r", newline="", encoding="utf8") as file:
        reader = csv.reader(file, delimiter=",")
        for row in reader:
            # Skips the title row and puts the rest into lists
            if row[0] != "ASIN":
                asin_csv.append(row[0])
            if row[1] != "Price":
                price_csv.append(row[1])


def Get_Amazon_Info(asin_list, price_list):
    # Slow down reCaptcha settings
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(
        options=options, executable_path=ChromeDriverManager().install())

    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                           "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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
            while True:
                try:
                    asin_textbox = driver.find_element_by_css_selector(
                        asin_cstm)

                    submit_asin_button = driver.find_element_by_css_selector(
                        submit_asin_cstm)

                    break
                except NoSuchElementException:
                    time.sleep(.25)

            asin_textbox.send_keys(asin)
            submit_asin_button.click()

            while True:
                try:
                    cog_textbox = driver.find_element_by_css_selector(
                        cost_goods_cstm)
                    misc_cog_textbox = driver.find_element_by_css_selector(
                        misc_cost_goods_cstm)
                    break
                except NoSuchElementException:
                    time.sleep(.25)

            cog_textbox.send_keys(woot_price)
            # misc_cog_textbox.send_keys()

            # Collect the Amazon info
            matches = ["#", ",", "(", ")"]
            matches_found = 0

            for td in driver.find_elements_by_css_selector("td"):
                if any(x in td.text for x in matches):
                    if matches_found == 0:
                        sales_rank = td.text
                        print('sales: ' + str(matches_found))
                    if matches_found == 1:
                        total_reviews = td.text
                        print('total reviews: ' + str(matches_found))

                    matches_found += 1
                    print('match found: ' + td.text)

                if " offers" in td.text:
                    offers = td.text

            print(sales_rank)
            print(total_reviews)
            time.sleep(1)

            html_source = driver.page_source

            Func = open("GFG-1.html", "w")

            # Adding input data to the HTML file
            Func.write(html_source)

            # Saving the data into the HTML file
            Func.close()

            for foobar in driver.find_elements_by_xpath("kat-label"):
                print(foobar.text)
                print('-------')

            cpu = driver.find_element_by_class_name(cpu_xpath).text
            net_unit_profit = driver.find_element_by_xpath(
                net_unit_profit_xpath).text
            amazon_fees = driver.find_element_by_xpath(amazon_fees_xpath).text


Pull_ASIN()
Get_Amazon_Info(asin_csv, price_csv)
