# Import required modules
import configparser
import time
import os
import csv
from os import listdir
from os.path import isfile, join
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime

script_dir = os.path.dirname(__file__)

# Import Amazon credneitals into local dictionary
config = configparser.RawConfigParser()
rel_path = "../../creds.cfg"
creds_file_path = os.path.join(script_dir, rel_path)
config.read(creds_file_path)

amazon_credentials = dict(config.items("Amazon_Credentials"))

user_email = amazon_credentials["amazon_user"]
user_pass = amazon_credentials["amazon_pass"]

# CSV asin file and website url - grab most recent file
folder = "exports"

appr_files = {}
date_keys = []

temp_path = os.path.join(script_dir, folder)
onlyfiles = [f for f in listdir(temp_path) if isfile(join(temp_path, f))]

# Search all files in export directory and place into list and dictionary
for file in onlyfiles:
    if "export_woot_bot" in file:
        date_key = int(file.split("_")[-1].split(".")[0])

        date_keys.append(date_key)
        appr_files[date_key] = file


sorted_csv_file = sorted(date_keys, reverse=True)[0]

# Combine latest file with rest of path
rel_path = folder + "/" + appr_files[sorted_csv_file]
main_csv_file = os.path.join(script_dir, rel_path)

# Export file
rel_path = folder + "/final-export{}.csv".format(
    datetime.today().strftime("%Y-%m-%d"))
export_csv_file = os.path.join(script_dir, rel_path)

master_list_file = {}

# CSV Import vars
asin_csv = []
price_csv = []
woot_name = []
woot_link = []

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
            if row[2] != "Name":
                woot_name.append(row[2])
            if row[3] != "URL":
                woot_link.append(row[3])


def Get_Amazon_Info(asin_list, price_list, woot_name, woot_link):
    global master_list_file

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

    # Wait for OTP to be entered if turned on
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

    for asin, woot_price, woot_name, woot_url in zip(asin_list, price_list, woot_name, woot_link):
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
            time.sleep(.5)
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

            time.sleep(.5)
            cog_textbox.send_keys(woot_price)
            # misc_cog_textbox.send_keys()

            # Collect the Amazon info
            matches = ["#", ",", "(", ")"]
            matches_found = 0

            for td in driver.find_elements_by_css_selector("td"):
                if any(x in td.text for x in matches):
                    if matches_found == 0:
                        sales_rank = td.text
                    if matches_found == 1:
                        total_reviews = td.text

                    matches_found += 1

                if " offers" in td.text:
                    offers = td.text

            prep_cpu = False
            prep_net_profit = False
            prep_net_margin = False

            cpu = []
            net_profit = []
            net_margin = []

            for label in driver.find_elements_by_tag_name("kat-label"):
                if prep_cpu:
                    cpu.append(label.get_attribute("text"))
                    prep_cpu = False
                if prep_net_profit:
                    net_profit.append(label.get_attribute("text"))
                    prep_net_profit = False
                if prep_net_margin:
                    net_margin.append(label.get_attribute("text"))
                    prep_net_margin = False

                if label.get_attribute("text") is not None:
                    if "Estimated cost per unit" in label.get_attribute("text"):
                        prep_cpu = True
                    if "Net profit per unit" in label.get_attribute("text"):
                        prep_net_profit = True
                    if "Net margin" in label.get_attribute("text"):
                        prep_net_margin = True

            #print(cpu[0], net_profit[0], net_margin[0])

            cpu = float(cpu[0].replace("$", "").replace(",", ""))
            net_profit = float(net_profit[0].replace("$", ""))
            net_margin = float(net_margin[0].replace("%", "").replace(",", ""))

            # Check if refurbished/multiple select option
            refurb = False
            if "refurbished" in woot_name.lower():
                refurb = True

            multi_select = False
            if "choice" in woot_name.lower():
                multi_select = True

            # Push all data to dictionary
            master_list_file[asin] = {
                "Name": woot_name,
                "ASIN": asin,
                "Refurbished": refurb,
                "Multi-Select": multi_select,
                "Price": woot_price,
                "Sales Rank": sales_rank,
                "Total Reviews": total_reviews,
                "Seller Offers": offers,
                "Cost per Unit": cpu,
                "Net Profit": net_profit,
                "Margin Percent": net_margin,
                "Woot Link": woot_url,
            }

            # Clear vars for next run
            cpu = ""
            net_profit = ""
            net_margin = ""
            sales_rank = ""
            total_reviews = ""

            driver.get(amazon_url)

    # Write the dictionary to the CSV file
    with open(export_csv_file, 'w') as f:
        write_head_once = True
        for asin, values in master_list_file.items():
            w = csv.DictWriter(f, values.keys())
            if write_head_once:
                w.writeheader()
            write_head_once = False
            w.writerow(values)


Pull_ASIN()
Get_Amazon_Info(asin_csv, price_csv, woot_name, woot_link)
