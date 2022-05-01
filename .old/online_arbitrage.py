#######################################################
######### USE THIS SCRIP TO BUILD THE EXCEL SHEET #####
#######################################################
import pandas as pd

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






