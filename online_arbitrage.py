#from operator import index
#import time
#from selenium import webdriver
import pandas as pd
#from openpyxl import load_workbook
#import time
# dataframe Name and Age columns
df = pd.DataFrame({'name': [],
                   'price': [],
                   'asin': [],
                   'amazon_price':[],
                   'net_profit': [],
                   'roi':[]})

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('demo.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Sheet1', index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.save()
#excel = pd.read_excel(r'C:\Users\nickm\OneDrive\Desktop\fba\woot.xlsx')
#driver = webdriver.Chrome()

#driver.get("https://www.woot.com/alldeals?ref=w_ngh_et_1") #get to woot
#time.sleep(2)

#product_id = driver.find_element_by_xpath('//*[@id="app-desktop"]/div/div/div[2]/div[2]/div/div/div/div[1]/div/div[1]')#locate the first product and click it
#product_id.click()
###############TODO############
#GET ITEM NAME, PRICE, ASIN NUMBER
#VERIFY CONDITION = NEW
#LOG NAME, PRICE, ASIN INTO AN EXCEL SHEET 

#csv = pd.read_csv(r'C:\Users\nimiller\Desktop\excel\moveandprovision.csv')
#time.sleep(2)
#price = driver.find_element_by_class_name('price').text
#time.sleep(2)





