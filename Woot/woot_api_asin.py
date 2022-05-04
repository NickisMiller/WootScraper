import requests
import os
import configparser
import csv
from datetime import datetime

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

params = {
    "page": '1',
}

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

print("Total Items Pulled: " + str(len(offer_ids["Items"])))

true_block_count = 0
for i, item in enumerate(offer_ids["Items"]):
    if((item["Condition"] is None) or ("new" in item["Condition"].lower())):
        if(true_block_count % 24 == 0 and true_block_count != 1 and true_block_count != 0):
            temp_offer_ids.append(item["OfferId"])

            # Divisable by 25 - append temp list to main list
            preped_offer_ids.append(temp_offer_ids)
            temp_offer_ids = []
        else:
            temp_offer_ids.append(item["OfferId"])

        true_block_count += 1
    else:
        print("Skipping " + item["Condition"] + " item.")

    # Write remaining to list
    if(i == len(offer_ids["Items"])):
        preped_offer_ids.append(temp_offer_ids)


offer_lookup = {}

for i, offer_id_block in enumerate(preped_offer_ids):
    post_offer_ids = requests.post(
        url=post_request_ep, json=offer_id_block, headers=api_key)
    block_return = post_offer_ids.json()

    for item in block_return:
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
    print("Block completed.")

    if(i > 0):
        write_head_once = False
        open_type = "a"
    else:
        write_head_once = True
        open_type = "w"

    with open(file_name_save, open_type) as f:
        for asin, values in offer_lookup.items():
            w = csv.DictWriter(f, values.keys())
            if write_head_once:
                w.writeheader()
            write_head_once = False
            w.writerow(values)

    # Clear dictionary for next block
    offer_lookup.clear()

print("Complete.")
