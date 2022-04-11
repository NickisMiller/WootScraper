from asyncio.windows_events import NULL
import pandas as pd
from openpyxl import load_workbook
from selenium import webdriver
import time


driver = webdriver.Chrome()
driver.get("https://www.woot.com/alldeals?ref=w_ngh_et_1")
time.sleep(3)


#aTagsInLi = driver.find_elements_by_css_selector('a')
for a in driver.find_elements_by_css_selector('a'):
    href = a.get_attribute('href')   
    if 'woot.com/offers/' in href:
        time.sleep(2)     
        driver.get(href)
        #time.sleep(2)
        name = driver.title
        print("Name is: ")
        print(name)
        #time.sleep(1)
        price = price = driver.find_element_by_class_name('price').text
        print(price)
        time.sleep(2)
        source = driver.page_source
        time.sleep(2)
        try:
            asin = source.split("Asin\":\"")[1].split("\"")[0]
        except IndexError:
            asin = 'null'
        time.sleep(2)
        print(asin)
        time.sleep(2)
        df = pd.DataFrame({'name': [name],
                   'price': [price],
                   'asin': [asin]})
        writer = pd.ExcelWriter('demo.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay')
        # try to open an existing workbook
        writer.book = load_workbook('demo.xlsx')
        # copy existing sheets
        writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
        # read existing file
        reader = pd.read_excel(r'demo.xlsx')
        # write out the new sheet
        df.to_excel(writer,index=False,header=False,startrow=len(reader)+1)
        writer.close()

        driver.implicitly_wait(2)
        driver.back()
        driver.implicitly_wait(2)

#https://www.profitguru.com/calculator/fba
#https://brickseek.com/        
#exit()


