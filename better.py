import os
import glob
import time
import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Temperature Sheet" ).sheet1



clock1 = "00:00"
clock2 = "00:30"

send_now = "19:00:00"

mainlowalarm = 3
baselowalarm = 3

alarm = 0

fromaddr = "cottagestatus@gmail.com"
toaddr = "erik.nikiforuk@dcmail.ca"

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir_1 = '/sys/bus/w1/devices/'
device_folder_1 = glob.glob(base_dir_1 + '28-0417c11d5*')[0]
device_file_1 = device_folder_1 + '/w1_slave'

def read_temp_raw_main():
    f = open(device_file_1, 'r')
    lines = f.readlines()
    f.close()
    return lines

base_dir_2 = '/sys/bus/w1/devices/'
device_folder_2 = glob.glob(base_dir_2 + '28-0417c1114*')[0]
device_file_2 = device_folder_2 + '/w1_slave'

def read_temp_raw_base():
    f = open(device_file_2, 'r')
    lines_1 = f.readlines()
    f.close()
    return lines_1

def read_temp_main():
    lines = read_temp_raw_main()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw_main()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def read_temp_base():
    lines_1 = read_temp_raw_base()
    while lines_1[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines_1 = read_temp_raw_base()
    equals_pos = lines_1[1].find('t=')
    if equals_pos != -1:
        temp_string = lines_1[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def update_spread():
    now = datetime.datetime.now()
    times = now.strftime("%Y/%m/%d %H:%M:%S")
    nextrow = sheet.row_count + 1
    try:
        sheet.update_cell(nextrow,1,times)
        sheet.update_cell(nextrow,2,read_temp_base())
        sheet.update_cell(nextrow,3,read_temp_main())
    except TypeError as e:
        sheet.add_rows(1)
        sheet.update_cell(nextrow,1,times)
        sheet.update_cell(nextrow,2,read_temp_base())
        sheet.update_cell(nextrow,3,read_temp_main())

while True:
	if read_temp_base() >= baselowalarm and read_temp_main() >= mainlowalarm and alarm == 1:
		alarm = 0
		os.remove('/home/pi/Desktop/Cottage/alarm.csv')
		f = open('alarm.csv', 'a')
		f.write(" ")
		f.close()


	if read_temp_base() <= baselowalarm or read_temp_main() <= mainlowalarm:
                    if alarm == 0:
                        os.remove('/home/pi/Desktop/Cottage/alarm.csv')
                        alarm = 1
                        basetemp = read_temp_base()
                        maintemp = read_temp_main()
                        f=open('alarm.csv', 'a')
                        outalarm = str(alarm)+"\n"+str(basetemp)+"\n"+str(maintemp)
                        f.write(outalarm)
                        f.close()

                        msg = MIMEMultipart()

                        msg['From'] = fromaddr
                        msg['To'] = toaddr
                        msg['Subject'] = "COTTAGE ALERT"

                        body = "IMPORTANT!\n\nThe cottage is in alarm state, Temperature is too low!\n\nBasement Temperature = "+str(basetemp)+" Degrees Celsius\n\nMain Floor Temperature = "+str(maintemp)+" Degrees Celcius"

                        msg.attach(MIMEText(body, 'plain'))

                        filename = "alarm.csv"
                        attachment = open("/home/pi/Desktop/Cottage/alarm.csv", "rb")

                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload((attachment).read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

                        msg.attach(part)

                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(fromaddr, "1100sandpoint")
                        text = msg.as_string()
                        server.sendmail(fromaddr, toaddr, text)
                        server.quit()
