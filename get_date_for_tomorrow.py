#! /usr/bin/python3.8

import requests
import smtplib
import datetime
import json

from config import *


request_url = "https://rdv.snct.lu/rdvct/appointment/nextAvailable/5"
request_data = {
    "vehicleTypeId": vehicle_type,
    "userType": "PRIVATE",
    "appointmentType": "REGULAR",
    "siteId": None,
}

site_data = {
    2: 'Sandweiler',
    3: 'Esch',
}

_buffer = datetime.datetime.today() + datetime.timedelta(hours=2)
window_start = datetime.datetime(year=_buffer.year, month=_buffer.month, day=_buffer.day)
window_stop = window_start + datetime.timedelta(hours=window_size*24)

slots = []
# Make a request per site
for site_id in site_selection:
    request_data['siteId'] = site_id
    request = requests.post(request_url, json=request_data, verify=False)
    slots += request.json()

options = []
# Go over responses and check matching dates
for slot in slots:
    date = datetime.datetime.strptime(slot['appointmentDay'], '%Y-%m-%d')
    time = datetime.datetime.strptime(slot['expectedSlot'], '%HH%M')

    rdv = datetime.datetime(day=date.day, year=date.year, month=date.month, hour=time.hour, minute=time.minute)
    option = str(rdv) + ' @ ' + site_data[slot['siteId']]
    print(option)
    if rdv >= window_start and rdv <= window_stop:
        options.append(option)


if options:
    try:
        smtpobj = smtplib.SMTP(email_host, email_port)
        smtpobj.starttls()
        smtpobj.login(sender_email, sender_password)

        header = ['From: ' + sender_email , 'To: ' + recipient_email, 'Subject: SNCT RDV', ]
        message = '\n'.join(header + options)

        smtpobj.sendmail(sender_email, recipient_email , message)
        smtpobj.quit()

        print('Message send!')
        print('My work here is done.')
    except Exception:
        print('Failed to send message')
        print('Please check the configuration')
        exit(1)

