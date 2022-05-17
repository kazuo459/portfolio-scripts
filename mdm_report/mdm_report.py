#!/usr/bin/env python3


# --------------- ENVIRONMENT SETUP --------------- #

# Date
import time
from datetime import date
import datetime

# Pandas
import pandas as pd
pd.options.mode.chained_assignment = None

# Requests
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# TQDM
from tqdm import tqdm

# --------------- GLOBAL VARIABLES --------------- #

# DateTime
NOW = datetime.datetime.now()
CURRENT_YEAR = NOW.year
TODAY = date.today()
today_list = []
today_list.append(TODAY.strftime('%Y'))
today_list.append(TODAY.strftime('%m'))
today_list.append(TODAY.strftime('%d'))
# Convert to int
for n, i in enumerate(today_list):
    today_list[n] = int(i)

# --------------- LOCAL VARIABLES --------------- #

jamf_url = input('Enter your Jamf API URL: ')
username = input('Enter your Jamf API username: ')
password = input('Enter your Jamf API password: ')

# --------------- FUNCTIONS --------------- #

# MDM Functions
def mdm_get_token(jamf_url, username, password):
    successful = False
    attempts = 0
    while successful == False:
        try:
            response = requests.post(
                url=f"{jamf_url}/api/v1/auth/token",
                headers={"accept": "application/json"},
                auth=HTTPBasicAuth(f'{username}', f'{password}'),
                verify=False,
            )
            response.raise_for_status()
            data = response.json()
            token = data['token']
            return token
        except requests.exceptions.HTTPError as e:
            attempts += 1
            if attempts >= 10:
                print("Could not complete after 10 attempts.")
                successful = True
        else:
            successful = True


def mdm_get_all_computer_data(jamf_url):
    endpoint = f"{jamf_url}/api/preview/computers"
    results = mdm_get_request_jamf_pro(token, endpoint)
    computers = results['results']
    return computers


def mdm_get_all_mobile_device_general_data(jamf_url):
    endpoint = f"{jamf_url}/JSSResource/mobiledevices"
    results = mdm_get_request_jamf_classic_json(username, password, endpoint)
    mobile_devices = results['mobile_devices']
    return mobile_devices


def mdm_get_computer_data_by_id(jamf_url, device_id):
    endpoint = f"{jamf_url}/JSSResource/computers/id/{device_id}"
    results = mdm_get_request_jamf_classic_json(username, password, endpoint)
    computer = results['computer']
    return computer


def mdm_get_mobile_device_data_by_id(jamf_url, device_id):
    endpoint = f"{jamf_url}/JSSResource/mobiledevices/id/{device_id}"
    results = mdm_get_request_jamf_classic_json(username, password, endpoint)
    mobile_device_data = results['mobile_device']
    return mobile_device_data


def mdm_get_request_jamf_classic_json(username, password, endpoint):
    headers = {'accept': 'application/json'}
    successful = False
    attempts = 0
    while successful == False:
        try:
            response = requests.get(
                url=endpoint,
                auth=HTTPBasicAuth(f'{username}', f'{password}'),
                headers=headers,
                verify=False,
            )
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.HTTPError as e:
            attempts += 1
            if attempts >= 10:
                successful = True
        else:
            success = True


def mdm_get_request_jamf_pro(token, endpoint):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    successful = False
    attempts = 0
    while successful == False:
        try:
            response = requests.get(
                url=endpoint,
                headers=headers,
                verify=False,
            )
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.HTTPError as e:
            attempts += 1
            if attempts >= 10:
                print("Could not complete after 10 attempts.")
                successful = True
        else:
            success = True


# Program Functions
def prog_convert_mb_to_gb(mb):
    gb = int(mb) / 1024
    gb = int(gb)
    return gb


# --------------- PROGRAM START --------------- #

# Get MDM token for Jamf Pro environment
token = mdm_get_token(jamf_url, username, password)

# Generate Computer Report
print("\nStarting Computer Report")

# Get all computer data from MDM
print("Getting all computer data...")
computers = mdm_get_all_computer_data(jamf_url)
number_of_computers = len(computers)
print(f"Total number of computers found: {number_of_computers}")

# Create empty dict that will become dataframe
data = {
    'Apple Silicon': [],
    'Battery Capacity': [],
    'Building': [],
    'Department': [],
    'Email': [],
    'Filevault Status': [],
    'Full Name': [],
    'Gatekeeper Status': [],
    'ID': [],
    'IP Address': [],
    'Last Check In': [],
    'Last Enrollment': [],
    'Last Inventory Update': [],
    'Management Status': [],
    'MDM Expiration': [],
    'Model': [],
    'Model ID': [],
    'Name': [],
    'OS Version': [],
    'Position': [],
    'Processor': [],
    'Processor Architecture': [],
    'Processor Cores': [],
    'Ram MB': [],
    'Room': [],
    'Serial Number': [],
    'SIP Status': [],
    'Storage Available MB': [],
    'Storage Total MB': [],
    'UDID': [],
    'Username': [],
}

# Loop through each device, get device ID, and get additional data. Then, append to dict.
print("Looping through each computer to get additional data...")
for item in tqdm(range(number_of_computers)):
    # Get device id
    device_id = computers[item]['id']
    data['ID'].append(device_id)
    # Use device id to get additional data
    computer = mdm_get_computer_data_by_id(jamf_url, device_id)
    try:
        # Append data to dict
        data['IP Address'].append(computer['general']['ip_address'])
        data['Management Status'].append(computer['general']['management_status']['enrolled_via_dep'])
        data['Name'].append(computer['general']['name'])
        data['Serial Number'].append(computer['general']['serial_number'])
        data['UDID'].append(computer['general']['udid'])
        data['Last Inventory Update'].append(computer['general']['report_date'])
        data['Last Check In'].append(computer['general']['last_contact_time'])
        data['Last Enrollment'].append(computer['general']['last_enrolled_date_utc'])
        data['MDM Expiration'].append(computer['general']['mdm_profile_expiration_utc'])
        data['Username'].append(computer['location']['username'])
        data['Full Name'].append(computer['location']['realname'])
        data['Email'].append(computer['location']['email_address'])
        data['Position'].append(computer['location']['position'])
        data['Department'].append(computer['location']['department'])
        data['Building'].append(computer['location']['building'])
        data['Room'].append(computer['location']['room'])
        data['Model'].append(computer['hardware']['model'])
        data['Model ID'].append(computer['hardware']['model_identifier'])
        data['OS Version'].append(computer['hardware']['os_version'])
        data['Processor'].append(computer['hardware']['processor_type'])
        data['Apple Silicon'].append(computer['hardware']['is_apple_silicon'])
        data['Processor Architecture'].append(computer['hardware']['processor_architecture'])
        data['Processor Cores'].append(computer['hardware']['number_cores'])
        data['Ram MB'].append(computer['hardware']['total_ram_mb'])
        data['Battery Capacity'].append(computer['hardware']['battery_capacity'])
        data['SIP Status'].append(computer['hardware']['sip_status'])
        data['Gatekeeper Status'].append(computer['hardware']['gatekeeper_status'])
        data['Storage Total MB'].append(computer['hardware']['storage'][0]['drive_capacity_mb'])
        data['Storage Available MB'].append(computer['hardware']['storage'][0]['partitions'][0]['available_mb'])
        data['Filevault Status'].append(computer['hardware']['storage'][0]['partitions'][0]['filevault_status'])
    except IndexError:
        pass
    except KeyError:
        pass
    # If an attribute was skipped due to IndexError or KeyError, add a blank entry, which will become nan value
    correct_length = len(data['ID'])
    for list in data:
        target_list = data[list]
        if len(target_list) != correct_length:
            target_list.append('')

# Generate additional columns of formatted data
print("Generating additional columns of data...")
# Days Since Last Check In
# Start by creating empty list in data dict
data['Days Since Last Check In'] = []
# Loop through 'Last Check In'
for item in data['Last Check In']:
    if item == '':
        data['Days Since Last Check In'].append('')
    else:
        # Pull date from item
        just_date = item[:10]
        just_date_list = just_date.split('-')
        # Convert each item in list to int
        for n, i in enumerate(just_date_list):
            just_date_list[n] = int(i)
        # Get total days from today minus last contact date
        d0 = date(just_date_list[0], just_date_list[1], just_date_list[2])
        d1 = date(today_list[0], today_list[1], today_list[2])
        delta = d1 - d0
        data['Days Since Last Check In'].append(delta.days)

# Days Since Last Enrollment
data['Days Since Last Enrollment'] = []
for item in data['Last Enrollment']:
    if item == '':
        data['Days Since Last Enrollment'].append('')
    else:
        # Pull date from item
        just_date = item[:10]
        just_date_list = just_date.split('-')
        # Convert each item in list to int
        for n, i in enumerate(just_date_list):
            just_date_list[n] = int(i)
        # Get total days from today minus last contact date
        d0 = date(just_date_list[0], just_date_list[1], just_date_list[2])
        d1 = date(today_list[0], today_list[1], today_list[2])
        delta = d1 - d0
        data['Days Since Last Enrollment'].append(delta.days)

# Days Since Last Inventory Update
data['Days Since Last Inventory Update'] = []
for item in data['Last Inventory Update']:
    if item == '':
        data['Days Since Last Inventory Update'].append('')
    else:
        # Pull date from item
        just_date = item[:10]
        just_date_list = just_date.split('-')
        # Convert each item in list to int
        for n, i in enumerate(just_date_list):
            just_date_list[n] = int(i)
        # Get total days from today minus last contact date
        d0 = date(just_date_list[0], just_date_list[1], just_date_list[2])
        d1 = date(today_list[0], today_list[1], today_list[2])
        delta = d1 - d0
        data['Days Since Last Inventory Update'].append(delta.days)

# Computer Year
# Start by creating empty list in data dict
data['Year'] = []
# Loop through 'Model'
for item in data['Model']:
    if item == '':
        data['Year'].append('')
    else:
        # Split Model into list
        list = item.split()
        for char in list:
            if char[0:2] == '20':
                new_char = char[0:4]
                # Append to year list
                data['Year'].append(new_char)
            elif char[1:3] == '20':
                new_char = char[1:5]
                data['Year'].append(new_char)

# Ram GB
data['Ram GB'] = []
for item in data['Ram MB']:
    if item == '':
        data['Ram GB'].append('')
    else:
        mb = item
        gb = prog_convert_mb_to_gb(mb)
        data['Ram GB'].append(gb)

# Storage Available GB
data['Storage Available GB'] = []
for item in data['Storage Available MB']:
    if item == '':
        data['Storage Available GB'].append('')
    else:
        mb = item
        gb = prog_convert_mb_to_gb(mb)
        data['Storage Available GB'].append(gb)

# Storage Total GB
data['Storage Total GB'] = []
for item in data['Storage Total MB']:
    if item == '':
        data['Storage Total GB'].append('')
    else:
        mb = item
        gb = prog_convert_mb_to_gb(mb)
        data['Storage Total GB'].append(gb)

# Save computer report to Box
print("Saving MDM Computer Report to Box...")
df = pd.DataFrame.from_dict(data)
df = df.reindex(sorted(df.columns), axis=1)
df = df.astype(object)
df.to_csv("mdm_computer_report.csv", index=False)
df.to_csv(f"{TODAY}_mdm_computer_report.csv", index=False)
# Create copy of dataframe to potentially reference later in script
current_computer_report_df = df.copy()

# MOBILE DEVICE REPORT
print("\nStarting Mobile Device Report")

# Get all mobile device data
print("Getting all mobile device data...")
mobile_devices = mdm_get_all_mobile_device_general_data(jamf_url)

# Get total number of devices
number_of_mobile_devices = len(mobile_devices)
print(f"Total number of mobile devices found: {number_of_mobile_devices}")

# Create empty dict that will become dataframe
data = {
    'Available MB': [],
    'Battery Level': [],
    'Building': [],
    'Capacity MB': [],
    'Carrier': [],
    'Department': [],
    'Device Name': [],
    'Email Address': [],
    'Enrollment Method': [],
    'ICCID': [],
    'ID': [],
    'IMEI': [],
    'Last Enrollment UTC': [],
    'Last Inventory Update': [],
    'Model': [],
    'Model Identifier': [],
    'Model Number': [],
    'Name': [],
    'Passcode Status': [],
    'Position': [],
    'Phone Number': [],
    'OS Build': [],
    'OS Version': [],
    'Percentage Used': [],
    'Room': [],
    'Serial Number': [],
    'UDID': [],
    'Username': [],
}
print("Looping through each mobile device to get additional data...")
# Loop through each device, get device ID, and get additional data. Then, append to dict.
for item in tqdm(range(number_of_mobile_devices)):
    # Get device id
    device_id = mobile_devices[item]['id']
    data['ID'].append(device_id)
    # Use device id to get additional data
    device_data = mdm_get_mobile_device_data_by_id(jamf_url, device_id)
    try:
        # Append data to data dict
        data['Available MB'].append(device_data['general']['available_mb'])
        data['Battery Level'].append(device_data['general']['battery_level'])
        data['Building'].append(device_data['location']['building'])
        data['Capacity MB'].append(device_data['general']['capacity_mb'])
        data['Carrier'].append(device_data['network']['home_carrier_network'])
        data['Department'].append(device_data['location']['department'])
        data['Device Name'].append(device_data['general']['device_name'])
        data['Email Address'].append(device_data['location']['email_address'])
        data['Enrollment Method'].append(device_data['general']['enrollment_method'])
        data['ICCID'].append(device_data['network']['iccid'])
        data['IMEI'].append(device_data['network']['imei'])
        data['Last Enrollment UTC'].append(device_data['general']['last_enrollment_utc'])
        data['Last Inventory Update'].append(device_data['general']['last_inventory_update'])
        data['Model'].append(device_data['general']['model'])
        data['Model Identifier'].append(device_data['general']['model_identifier'])
        data['Model Number'].append(device_data['general']['model_number'])
        data['Name'].append(device_data['location']['realname'])
        data['OS Build'].append(device_data['general']['os_build'])
        data['OS Version'].append(device_data['general']['os_version'])
        data['Passcode Status'].append(device_data['security']['passcode_present'])
        data['Percentage Used'].append(device_data['general']['percentage_used'])
        data['Phone Number'].append(device_data['general']['phone_number'])
        data['Position'].append(device_data['location']['position'])
        data['Room'].append(device_data['location']['room'])
        data['Serial Number'].append(device_data['general']['serial_number'])
        data['UDID'].append(device_data['general']['udid'])
        data['Username'].append(device_data['location']['username'])
    except IndexError:
        pass
    except KeyError:
        pass
    # If an attribute was skipped due to IndexError or KeyError, add a blank entry
    correct_length = len(data['ID'])
    for list in data:
        target_list = data[list]
        if len(target_list) != correct_length:
            target_list.append('')

# Perform clean up of data
print("Performing cleanup of data...")

# Format ICCIDs
formatted_iccid_list = []
for item in data['ICCID']:
    if item == '':
        formatted_iccid_list.append('')
    else:
        formatted_iccid = item.replace(' ','')
        formatted_iccid_list.append(formatted_iccid)
data['ICCID'] = formatted_iccid_list

# Format IMEI
formatted_imei_list = []
for item in data['IMEI']:
    if item == '':
        formatted_imei_list.append('')
    else:
        formatted_imei = item.replace(' ', '')
        formatted_imei_list.append(formatted_imei)
data['IMEI'] = formatted_imei_list

# Format Phone Number
formatted_phone_number_list = []
for item in data['Phone Number']:
    # If entry is empty, skip.
    if item == '' or item == '00000000000':
        formatted_phone_number_list.append('')
    else:
        # Remove '+' if it exists
        if item[0] == '+':
            formatted_phone_number = item[2:]
        # Remove '1' from phone number
        if item[0] == '1':
            formatted_phone_number = item[1:]
        formatted_phone_number_list.append(formatted_phone_number)
data['Phone Number'] = formatted_phone_number_list

# Generate additional columns of formatted data
print("Generating additional columns of data...")

# Available GB
data['Available GB'] = []
for item in data['Available MB']:
    if item == '':
        data['Available GB'].append('')
    else:
        mb = item
        gb = prog_convert_mb_to_gb(mb)
        data['Available GB'].append(gb)

# Capacity GB
data['Capacity GB'] = []
for item in data['Capacity MB']:
    if item == '':
        data['Capacity GB'].append('')
    else:
        mb = item
        gb = prog_convert_mb_to_gb(mb)
        data['Capacity GB'].append(gb)

# Days Since Last Inventory Update
# Start by creating empty list in data dict
data['Days Since Last Inventory Update'] = []
# Loop through 'Last Check In'
for item in data['Last Inventory Update']:
    if item == '':
        data['Days Since Last Inventory Update'].append('')
    else:
        last_inventory_update = item
        # Get just the date from last inventory update
        date_list = str.split(last_inventory_update)
        # Filter down date list to what we need
        just_date_list = []
        just_date_list.append(date_list[1])
        just_date_list.append(date_list[2])
        just_date_list.append(date_list[3])
        # Convert month string to number string
        for n, i in enumerate(just_date_list):
            if i == 'January':
                just_date_list[n] = '1'
            elif i == 'February':
                just_date_list[n] = '2'
            elif i == 'March':
                just_date_list[n] = '3'
            elif i == 'April':
                just_date_list[n] = '4'
            elif i == 'May':
                just_date_list[n] = '5'
            elif i == 'June':
                just_date_list[n] = '6'
            elif i == 'July':
                just_date_list[n] = '7'
            elif i == 'August':
                just_date_list[n] = '8'
            elif i == 'September':
                just_date_list[n] = '9'
            elif i == 'October':
                just_date_list[n] = '10'
            elif i == 'November':
                just_date_list[n] = '11'
            elif i == 'December':
                just_date_list[n] = '12'
        # Convert date list to integer
        for n, i in enumerate(just_date_list):
            just_date_list[n] = int(i)
        # Reorder list
        date_order = [2, 0, 1]
        just_date_list = [just_date_list[i] for i in date_order]
        # Get total days from today minus last check in date
        d0 = date(just_date_list[0], just_date_list[1], just_date_list[2])
        d1 = date(today_list[0], today_list[1], today_list[2])
        delta = d1 - d0
        days = delta.days
        days_int = int(days)
        data['Days Since Last Inventory Update'].append(days_int)

# Save Mobile Device Report to Box
print("Saving MDM Mobile Device Report to Box...")
df = pd.DataFrame.from_dict(data)
df = df.reindex(sorted(df.columns), axis=1)
df = df.astype(object)
df.to_csv("mdm_mobile_device_report.csv", index=False)
df.to_csv(f"{TODAY}_mdm_mobile_device_report.csv", index=False)
# Create copy of dataframe for potential future reference
current_mobile_device_report_df = df.copy()