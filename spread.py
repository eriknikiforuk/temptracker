#make suee to do
#pip install gspread oauth2client

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("Temperature Sheet" ).sheet1

# Extract and print all of the values
basetemp = 221
maintemp = -244
now = datetime.datetime.now()
times = now.strftime("%Y/%m/%d %H:%M:%S")

# Spreadsize = sheet.row_count
nextrow = sheet.row_count + 1
print(sheet.row_count)
# row =["2018/02/23 22:47:01","42","333"]
# sheet.insert_row(row, Spreadsize+1)

r = 4
try:
    sheet.update_cell(nextrow,1,times)
    sheet.update_cell(nextrow,2,maintemp)
    sheet.update_cell(nextrow,3,basetemp)
except TypeError as e:
    sheet.add_rows(1)
    sheet.update_cell(nextrow,1,times)
    sheet.update_cell(nextrow,2,maintemp)
    sheet.update_cell(nextrow,3,basetemp)
    # sheet.append_row(times,maintemp,basetemp)
