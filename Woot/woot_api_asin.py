import requests
import os
import configparser
import csv
from datetime import datetime
import time

script_dir = os.path.dirname(__file__)

# Import Woot API credneitals into local dictionary
rel_path = "../../creds.cfg"
creds_file_path = os.path.join(script_dir, rel_path)

config = configparser.RawConfigParser()
config.read(creds_file_path)
api_key = dict(config.items("Woot_API_Key"))

# Export file name
rel_path = "exports/export_woot_bot_{}.csv".format(
    int(round(datetime.now().timestamp())))
file_name_save = os.path.join(script_dir, rel_path)

# Woot categories to search
category_select = 1

woot_categories = [
    "All",  # 0
    "Clearance",  # 1
    "Computers",  # 2
    "Electronics",  # 3
    "Featured",  # 4
    "Home",  # 5
    "Gourmet",  # 6
    "Shirts",  # 7
    "Sports",  # 8
    "Tools",  # 9
    "Wootoff",  # 10
]

for k, j in enumerate(range(200), 1):
    # If you want to only search a specific page: un-comment param
    params = {
        "page": k
    }

    # Woot get and post end points
    get_request_ep = "https://developer.woot.com/feed/{}".format(
        woot_categories[category_select])
    post_request_ep = "https://developer.woot.com/getoffers"

    # Post requests allow 25 OfferIds per request
    preped_offer_ids = []
    temp_offer_ids = []

    # Get request for available offer ids
    get_offer_ids = requests.get(
        url=get_request_ep, params=params, headers=api_key)
    offer_ids = get_offer_ids.json()

    true_block_count = 0
    for i, item in enumerate(offer_ids["Items"]):

        # If no condition given or 'new' is in the condition field - continue
        if((item["Condition"] is None) or ("new" in item["Condition"].lower())):

            # Check if divisable by 24 and not equal to 1 or 0
            if(true_block_count % 15 == 0 and true_block_count != 1 and true_block_count != 0):
                # Append item to temp list
                temp_offer_ids.append(item["OfferId"])

                # Divisable by 25 - append temp list to main list
                preped_offer_ids.append(temp_offer_ids)
                temp_offer_ids = []
            else:
                # Append item to temp list
                temp_offer_ids.append(item["OfferId"])

            # Get true block count after 'new' or 'none' if statement filter
            true_block_count += 1
        else:

            # Print what item condition is being skipped
            print("Skipping " + item["Condition"] + " item.")

        # Write remaining items to list
        if(i == len(offer_ids["Items"])):
            preped_offer_ids.append(temp_offer_ids)

    print("Total Items Pulled: " + str(len(offer_ids["Items"])))

    offer_lookup = {}
    print(preped_offer_ids)
    # Send OfferIds back to woot to get asin and pricing information
    for i, offer_id_block in enumerate(preped_offer_ids):

        while True:
            # Send post request to woot api
            post_offer_ids = requests.post(
                url=post_request_ep, json=offer_id_block, headers=api_key)
            block_return = post_offer_ids.json()
            print('running')

            if("message" in block_return):
                if block_return["message"] != "Internal server error" and block_return["message"] != "Endpoint request timed out":
                    break
                else:
                    time.sleep(2)
                    print("\n\nNew Error:\n")
                    print(offer_id_block)
            else:
                break

        # If error in json return - display error to user
        if("message" in block_return):
            print("****")
            print(block_return)
            print("Block size (should be 25): " + str(len(offer_id_block)))
            print("****")

        # Send json return data to dictionary for output to csv file
        for item in block_return:
            print(item)
            offer_lookup[item["Id"]] = {
                "Id": item["Id"],
                "Asin": item["Items"][0]["Asin"],
                "FullTitle": item["FullTitle"],
                "Price": item["Items"][0]["SalePrice"],
                "IsOfferLiveNow": item["IsOfferLiveNow"],
                "IsSoldOut": item["IsSoldOut"],
                "IsWootOff": item["IsWootOff"],
                "Items": item["Items"],
                "RemainingPercent": item["PercentageRemainingBlurred"],
                "PurchaseLimit": item["PurchaseLimit"],
                "Url": item["Url"],
            }

        print("Block completed. ({})/{}".format(i+1, len(preped_offer_ids)))

        # If this is the first loop, write the header row and change to writing mode
        if(i > 0 and j == 0):
            write_head_once = False
            open_type = "a"  # append mode
        else:
            write_head_once = True
            open_type = "w"  # write mode

        # Push the dictionary data to the csv file - every 25 items (block)
        with open(file_name_save, open_type, encoding="utf-8") as f:
            for asin, values in offer_lookup.items():
                w = csv.DictWriter(f, values.keys())
                if write_head_once:
                    w.writeheader()
                write_head_once = False
                w.writerow(values)

        # Clear dictionary for next block
        offer_lookup.clear()

        print(" ------- Block End ------ ")

    print("Complete.")
