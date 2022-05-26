# -- MODULES -- #

# Date
import datetime
from datetime import date

# Getpass
from getpass import getpass

# Packaging
import packaging
from packaging import version

# Pandas
import pandas as pd

# Requests
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#TQDM
from tqdm import tqdm


# -- VARIABLES -- #

# Date / Time Variables
NOW = datetime.datetime.now()
CURRENT_YEAR = NOW.year
TODAY = date.today()

# Jamf Environment
JAMF_URL = '<insert_your_jamf_pro_url>'
USERNAME = input("Enter your Jamf Pro Username: ")
PASSWORD = getpass()


# -- GENERAL REQUEST FUNCTIONS -- #

def mdm_get_request_jamf_classic_json(endpoint):
    headers = {'accept': 'application/json'}
    successful = False
    attempts = 0
    while successful == False:
        try:
            response = requests.get(
                url=endpoint,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                headers=headers,
                verify=False,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            attempts += 1
            if attempts >= 10:
                successful = True
        else:
            result = response.json()
            return result


def mdm_get_request_jamf_classic_xml(endpoint):
    headers = {'accept': 'application/xml'}
    successful = False
    attempts = 0
    while successful == False:
        try:
            response = requests.get(
                url=endpoint,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                headers=headers,
                verify=False,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            attempts += 1
            if attempts >= 10:
                successful = True
        else:
            result = response.text
            return result


def mdm_get_request_jamf_pro(endpoint):
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
        except requests.exceptions.HTTPError as e:
            attempts += 1
            if attempts >= 10:
                print("Could not complete after 10 attempts.")
                successful = True
        else:
            result = response.json()
            return result


def mdm_get_token():
    successful = False
    attempts = 0
    while successful == False:
        try:
            response = requests.post(
                url=f"{JAMF_URL}/api/v1/auth/token",
                headers={"accept": "application/json"},
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                verify=False,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            attempts += 1
            if attempts >= 10:
                print("Could not complete after 10 attempts.")
                successful = True
        else:
            data = response.json()
            token = data['token']
            return token


# -- MOBILE DEVICE FUNCTIONS -- #


def mdm_get_all_mobile_device_general_data():
    endpoint = f"{JAMF_URL}/JSSResource/mobiledevices"
    results = mdm_get_request_jamf_classic_json(endpoint)
    mobile_devices = results['mobile_devices']
    return mobile_devices


def mdm_get_mobile_device_data_by_id(device_id):
    endpoint = f"{JAMF_URL}/JSSResource/mobiledevices/id/{device_id}"
    results = mdm_get_request_jamf_classic_json(endpoint)
    mobile_device_data = results['mobile_device']
    return mobile_device_data


# -- COMPUTER FUNCTIONS -- #


def mdm_get_all_computer_general_data():
    endpoint = f"{JAMF_URL}/api/preview/computers?page-size=1000"
    results = mdm_get_request_jamf_pro(endpoint)
    computers = results['results']
    return computers


def mdm_get_computer_data_by_id(device_id):
    endpoint = f"{JAMF_URL}/JSSResource/computers/id/{device_id}"
    results = mdm_get_request_jamf_classic_json(endpoint)
    computer = results['computer']
    return computer


# -- PROGRAM START -- #

token = mdm_get_token()


# COMPUTER REPORT

print("\nStarting Computer Report")

# Get all computer data from MDM
print("Getting all computer data...")
computers = mdm_get_all_computer_general_data()
number_of_computers = len(computers)
print(f"Total number of computers found: {number_of_computers}")

# Create empty dict
data = {
    'Apple Silicon': [],
    'Battery Capacity': [],
    'Building': [],
    'Department': [],
    'Email': [],
    'Enrollment DEP': [],
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
    computer = mdm_get_computer_data_by_id(device_id)
    try:
        # Append data to dict
        data['Enrollment DEP'].append(computer['general']['management_status']['enrolled_via_dep'])
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
    # If an attribute was skipped due to IndexError or KeyError, add a blank entry
    correct_length = len(data['ID'])
    for list in data:
        target_list = data[list]
        if len(target_list) != correct_length:
            target_list.append('')

print("Saving MDM Computer Report...")
df = pd.DataFrame.from_dict(data)
df = df.reindex(sorted(df.columns), axis=1)
df = df.astype(object)
df.to_csv(f"{TODAY}_mdm_computer_report.csv", index=False)

# Save dataframe to variable for audit reports later
current_computer_report_df = df.copy()


# MOBILE DEVICE REPORT

print("\nStarting Mobile Device Report")

# Get all mobile device data
print("Getting all mobile device data...")
mobile_devices = mdm_get_all_mobile_device_general_data()

# Get total number of devices
number_of_mobile_devices = len(mobile_devices)
print(f"Total number of mobile devices found: {number_of_mobile_devices}")

# Create empty dict
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
    'Last Enrollment': [],
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
    device_data = mdm_get_mobile_device_data_by_id(device_id)
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
        data['Last Enrollment'].append(device_data['general']['last_enrollment_utc'])
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

print("Saving MDM Mobile Device Report...")
df = pd.DataFrame.from_dict(data)
df = df.reindex(sorted(df.columns), axis=1)
df = df.astype(object)
df.to_csv(f"{TODAY}_mdm_mobile_device_report.csv", index=False)

# Save dataframe to variable for audit reports later
current_mobile_device_report_df = df.copy()


# -- AUDIT REPORTS -- #

# Mobile Devices with 80% or Higher Storage Being Used
print("\nMobile Devices with Full Storage:")
df = current_mobile_device_report_df.copy()
for idx, row in df.iterrows():
    percentage_used = row['Percentage Used']
    if percentage_used < 80:
        df.drop(idx, inplace=True)
df = df[['Device Name', 'Username', 'Serial Number', 'Percentage Used']]
print(df.to_string(index=False))

# Mobile Devices with 20% or Lower Battery Levels
print("\nMobile Devices with Low Battery:")
df = current_mobile_device_report_df.copy()
for idx, row in df.iterrows():
    battery_level = row['Battery Level']
    if battery_level > 20:
        df.drop(idx, inplace=True)
df = df[['Device Name', 'Username', 'Serial Number', 'Battery Level']]
print(df.to_string(index=False))

# Mobile Devices with out of date Software Version
print("\nMobile Devices with out of date software:")
min_os = '15.0'
df = current_mobile_device_report_df.copy()
for idx, row in df.iterrows():
    current_os_version = row['OS Version']
    if version.parse(current_os_version) >= version.parse(min_os):
        df.drop(idx, inplace=True)
df = df[['Device Name', 'Username', 'OS Version', 'Serial Number']]
print(df.to_string(index=False))


# -- PROGRAM END -- #