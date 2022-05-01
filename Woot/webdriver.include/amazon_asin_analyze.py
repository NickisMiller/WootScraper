# Import required modules
import configparser
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime

# Import Amazon credneitals into local dictionary
config = configparser.RawConfigParser()
config.read("/Users/codyheiser/Documents/AmazonSeller/Bots/creds.cfg")

amazon_credentials = dict(config.items("Amazon_Credentials"))

# CSV asin file and website url
main_csv_file = "export_woot_bot_1651300916.csv"
amazon_url = "https://sellercentral.amazon.com/revcal?ref=RC1&"

driver = webdriver.Chrome(ChromeDriverManager().install())

if __name__ == __main__:
    driver.get(amazon_url)
