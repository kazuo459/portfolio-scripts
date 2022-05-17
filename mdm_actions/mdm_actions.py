#!/usr/bin/env python3

# --------------- ENVIRONMENT SETUP --------------- #

# Getpass Module
import getpass

# Pandas module
import pandas as pd

# Requests Module
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# OS Module
import os

# Time Module
import time


# ---------- GLOBAL VARIABLES ---------- #

# Program Dictionary
PROGRAM_DICT = [
    {
        'option': '1',
        'purpose': 'Prepare Device in MDM Before Setup',
    },
    {
        'option': '2',
        'purpose': 'Update Assignment of Device in MDM',
        'options': [
            {
                'sub-option': '1',
                'description': 'Assign a Newly Set Up Device',
            },
            {
                'sub-option': '2',
                'description': 'Un-assign a Device and Remove from MDM',
            },
            {
                'sub-option': '3',
                'description': 'Re-assign a Device in MDM'
            }
        ]
    },
    {
        'option': '3',
        'purpose': 'Perform Management Actions on Device in MDM',
        'options': {
            'computer': [
                {
                    'action': '1',
                    'description': 'View Inventory Information for Device',
                },
                {
                    'action': '2',
                    'description': 'Remove an Item from Device (for troubleshooting purposes)',
                    'sub-actions': [
                        {
                            'sub-action': '1',
                            'description': 'Remove App Store Restriction',
                            'group_id': '',
                            'group_name': '[PROD] ALL | App Store Restriction | Exclusion',
                        },
                    ]
                },
                {
                    'action': '3',
                    'description': 'Re-add an Item from Device (for troubleshooting purposes)',
                    'sub-actions': [
                        {
                            'sub-action': '1',
                            'description': 'Re-add App Store Restriction',
                            'group_id': '',
                            'group_name': '[PROD] ALL | App Store Restriction | Exclusion',
                        },
                    ],
                },
            ],
            'mobile_device': [
                {
                    'action': '1',
                    'description': 'View User Inventory Information',
                },
                {
                    'action': '2',
                    'description': 'Perform Inventory Update',
                },
                {
                    'action': '3',
                    'description': 'View Completed, Pending, and Failed Commands',
                },
                {
                    'action': '4',
                    'description': 'Clear Pending and Failed Commands',
                },
                {
                    'action': '5',
                    'description': 'Activate Lost Mode for Device',
                },
                {
                    'action': '6',
                    'description': 'De-activate Lost Mode for Device',
                },
                {
                    'action': '7',
                    'description': 'Remove an Item from Device (for troubleshooting purposes)',
                    'sub-actions': [
                        {
                            'sub-action': '1',
                            'description': 'Remove WiFi Configuration Profile',
                            'group_id': '',
                            'group_name': '',
                        },
                        {
                            'sub-action': '2',
                            'description': 'Remove VPN Configuration Profile',
                            'group_id': '',
                            'group_name': '',
                        },
                        {
                            'sub-action': '3',
                            'description': 'Remove Home Screen Layout Configuration Profile',
                            'group_id': '',
                            'group_name': '',
                        },
                    ],
                },
                {
                    'action': '8',
                    'description': 'Re-add an Item from Device (for troubleshooting purposes)',
                    'sub-actions': [
                        {
                            'sub-action': '1',
                            'description': 'Re-add WiFi Configuration Profile',
                            'group_id': '',
                            'group_name': '',
                        },
                        {
                            'sub-action': '2',
                            'description': 'Re-add VPN Configuration Profile',
                            'group_id': '',
                            'group_name': '',
                        },
                        {
                            'sub-action': '4',
                            'description': 'Re-add Home Screen Layout Configuration Profile',
                            'group_id': '',
                            'group_name': '',
                        },
                    ],
                },
            ],
        },
    },
    {
        'option': '4',
        'purpose': 'Lookup Devices Issued to User',
        'options': [
            {
                'option': '1',
                'description': 'Lookup by User ID',
            },
            {
                'option': '2',
                'description': 'Lookup by User Name'
            },
        ]
    },
    {
        'option': '5',
        'purpose': 'Perform Device Audit',
    }
]
# Device Dictionary
DEVICE_DICT = [
{
        'option': '1',
        'device_type': 'Mac',
        'device_category': 'Computer',
        'usage_types': [
            {
                'option': '1',
                'usage_type': 'Personal Mac',
                'prestage_id': '',
            },
            {
                'option': '2',
                'usage_type': 'Shared Mac',
                'prestage_id': '175',
                'static_groups': [
                    {
                        'group_name': '',
                        'group_id': '',
                        'group_short_name': '',
                        'group_short_number': '',
                    },
                    {
                        'group_name': '',
                        'group_id': '',
                        'group_short_name': '',
                        'group_short_number': '',
                        'dri_dsid': '',
                    },
                ]
            },
        ],
    },
    {
        'option': '2',
        'device_type': 'iPad',
        'device_category': 'Mobile Device',
        'usage_types': [
            {
                'option': '1',
                'usage_type': 'Personal iPad',
                'prestage_id': '',
            },
            {
                'option': '2',
                'usage_type': 'Shared iPad',
                'prestage_id': '',
            },
        ],
    },
    {
        'option': '3',
        'device_type': 'iPhone',
        'device_category': 'Mobile Device',
        'usage_types': [
            {
                'option': '1',
                'usage_type': 'Personal iPhone',
                'prestage_id': '',
            },
            {
                'option': '2',
                'usage_type': 'Shared iPhone',
                'prestage_id': ''
            },
        ],
    },
]


# ---------- LOCAL VARIABLES ---------- #

local_user = getpass.getuser()
script_name = os.path.basename(__file__)
log = f"*{script_name} log:*\n" \
          f"User: {local_user}"
jamf_url = input("Enter your Jamf Pro Environment URL: ")
username = input("Enter your Jamf Pro username: ")
password = input("Enter your Jamf Pro password: ")


# ---------- FUNCTIONS ---------- #

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


# Program Functions

def prog_get_device_category(device_type):
    for item in DEVICE_DICT:
        if item['device_type'] == device_type:
            device_category = item['device_category']
    return device_category


def prog_get_prestage_id(usage_type):
    for category in DEVICE_DICT:
        for device in category['usage_types']:
            if usage_type == device['usage_type']:
                prestage_id = device['prestage_id']
    return prestage_id


def prog_prompt_for_serial_number():
    serial_number = ''
    serial_number_check = 'a'
    while serial_number != serial_number_check:
        serial_number = input("\n"
                              "Enter the Device Serial Number: ")
        serial_number_check = input("Re-enter the Device Serial Number: ")
    serial_number = serial_number.upper()
    return serial_number


def prog_prompt_for_device_type():
    device_type_input = ''
    device_type_input_check = 'a'
    print("\n")
    for item in DEVICE_DICT:
        print(f"({item['option']}) {item['device_type']}")
    while device_type_input != device_type_input_check:
        device_type_input = input("Enter the number for Device Type: ")
        device_type_input_check = input("Re-enter the number for Device Type: ")
    for item in DEVICE_DICT:
        if item['option'] == device_type_input:
            device_type = item['device_type']
    return device_type


def prog_prompt_for_usage_type(device_type):
    usage_type_input = ''
    usage_type_input_check = 'a'
    print("\n")
    for category in DEVICE_DICT:
        if device_type == category['device_type']:
            usage_type_list = category['usage_types']
    for item in usage_type_list:
        print(f"({item['option']}) {item['usage_type']}")
    while usage_type_input != usage_type_input_check:
        usage_type_input = input("Enter the number for Usage Type: ")
        usage_type_input_check = input("Re-enter number for the Usage Type: ")
    for item in usage_type_list:
        if item['option'] == usage_type_input:
            usage_type = item['usage_type']
    return usage_type



# ---------- PROGRAM START ---------- #


# Generate MDM token
token = mdm_get_token(jamf_url, username, password)


# Prompt for Purpose
purpose_input = ''
purpose_input_check = 'a'
while purpose_input != purpose_input_check:
    print("\n")
    for item in PROGRAM_DICT:
        print(f"({item['option']}) {item['purpose']}")
    purpose_input = input("Enter the number for what you'd like to do: ")
    purpose_input_check = input("Re-enter the number for what you'd like to do: ")
for item in PROGRAM_DICT:
    if item['option'] == purpose_input:
        purpose = item['purpose']

if purpose == 'Prepare Device in MDM Before Setup':

    # Prompt for Serial Number
    serial_number = prog_prompt_for_serial_number()

    # Prompt for Device Type
    device_type = prog_prompt_for_device_type()

    # Prompt for Usage Type
    usage_type = prog_prompt_for_usage_type(device_type)

    # Get Device Category
    device_category = prog_get_device_category(device_type)

    # Get PreStage ID
    prestage_id = prog_get_prestage_id(usage_type)

    # Prompt for reason
    description = ''
    while description == '':
        description = input("\nPlease enter a description of why you are initiating this request: ")

    # Generate Summary Header
    message_header = f"{message}\n" \
                     f"Purpose: {purpose}\n" \
                     f"Description: {description}\n" \
                     f"Device Type: {device_type}\n" \
                     f"Usage Type: {usage_type}\n" \
                     f"Serial Number: {serial_number}\n" \
                     f"*Activity*"

    message = message_header



























