from copy import deepcopy
import requests
import json
import subprocess
import ast
import os
from datetime import datetime, timedelta
import time
import pytz
import logging
import traceback

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Devices

from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from dotenv import load_dotenv

logger = logging.getLogger('views')

ttn_cache = {}
twilio_cache = {}

def home_view(request):
    return render(request, "home.html")

def ttn_view(request):
    # https://www.thethingsindustries.com/docs/the-things-stack/interact/api/#multi-step-actions

    load_dotenv()

    applications = subprocess.Popen(
    "ttn-lw-cli applications list",
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE, 
    shell=True
    )
    output, _ = applications.communicate()
    dict_str = output.decode("UTF-8")
    application_list = ast.literal_eval(dict_str)

    app_names = []
    for app in application_list:
        app_name = app["ids"]["application_id"]
        app_names.append(app_name)

    ttn_api_key = os.getenv('TTN_API_KEY')

    form_device_id = request.GET.get('device_id', False)
    form_device_eui = request.GET.get('device_eui', False)
    form_join_eui = request.GET.get('join_eui', False)

    application = request.GET.get('dropdown', False)

    ttn_post_url = 'https://symrec.eu1.cloud.thethings.industries/api/v3/applications/invalid/devices'

    if application is not False:
        ttn_post_url = 'https://symrec.eu1.cloud.thethings.industries/api/v3/applications/' + str(application) +'/devices'
    print(ttn_post_url)

    request_params = {
        "device_id": form_device_id ,
        "dev_eui": form_device_eui,
        "join_eui": form_join_eui
    }

    # To register a device newdev1 in application app1, first, register the DevEUI, JoinEUI and cluster addresses in the Identity Server. 
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + ttn_api_key,
        'Content-Type': 'application/json',
        'User-Agent': 'my-integration/my-integration-version'
    }
   
    data = {
        "end_device": {
            "ids": request_params,
            "join_server_address": "symrec.nam1.cloud.thethings.industries",
            "network_server_address": "symrec.nam1.cloud.thethings.industries",
            "application_server_address": "symrec.nam1.cloud.thethings.industries"
            },
        "field_mask": {
            "paths": [
                "join_server_address",
                "network_server_address",
                "application_server_address",
                "ids.dev_eui",
                "ids.join_eui"
            ]
        }
    }

    post_payload = json.dumps(data)
    print(post_payload)

    # TODO: input sanitation and add error message
    
    if not form_device_id or not form_device_eui or not form_join_eui:
        logger.debug("Form not completed yet")
        return render(request, "ttn.html", {"app_names": app_names})
    try:
        r = requests.post(ttn_post_url, data=post_payload, headers=headers)
        resp_json = r.json()
        logger.debug('r.status_code', r.status_code)
        print(f'r.text: {r.text}')

        if r.status_code == 200:
            return redirect("devices_view")
        else:
            return render(request, "ttn.html", {"error": resp_json['message'], "app_names": app_names})

    except Exception:
        logger.debug(f"Error: TTN Post.\n{traceback.format_exc()}")
        return render(request, "ttn.html", {"error": traceback.format_exc(), "app_names": app_names})


def getTTNDevices():

    applications = subprocess.Popen(
        "ttn-lw-cli applications list",
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        shell=True
    )
    output, _ = applications.communicate()
    dict_str = output.decode("UTF-8")
    application_list = ast.literal_eval(dict_str)

    devices_list = []

    # For each application-id, use it to get all associated TTN devices
    for app in application_list:
        app_name = app["ids"]["application_id"]
        app_devices = subprocess.Popen(
            "ttn-lw-cli end-device list --application-id " + app_name, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            shell=True
        )
        output, _ = app_devices.communicate()
        dict_str = output.decode("UTF-8")
        app_devices = ast.literal_eval(dict_str) 

        devices_list += (app_devices)


    for device in devices_list:
        device["device_network"] = "TTN"

        create_time = device["created_at"]
        create_time = datetime.strptime(create_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        device["created_at"] = create_time

        update_time = device["updated_at"]
        update_time = datetime.strptime(update_time, "%Y-%m-%dT%H:%M:%S.%fZ")

        # if update and create time are similar, they are probably the same
        if (update_time - create_time < timedelta(seconds=0.1)):
            device["updated_at"] = "Never"
        else:
            device["updated_at"] = create_time

    return devices_list

def getTwilioDevices():
    load_dotenv()
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    sims = client.supersim.v1.sims.list()
    devices_list = [
        {
            "device_network": "Twilio",
            "created_at": sim.date_created,
            "updated_at": sim.date_updated,
            "sid": sim.sid,
            "iccid": sim.iccid,
            "status": str(sim.status),
        } for sim in sims
    ]
    return devices_list


def devices_view(request):
    global ttn_cache, twilio_cache

    ttn_devices = getTTNDevices()
    twilio_devices = getTwilioDevices()

    ttn_cache = deepcopy(ttn_devices)
    twilio_cache = deepcopy(twilio_devices)

    # makes common list of devices to be displayed in one table in devices page
    combined_devices = []
    for device in ttn_devices:
        device["device_id"] = device["ids"]["device_id"]
        device["created_at"] = device["created_at"].replace(tzinfo=None)
        combined_devices.append(device)

    for device in twilio_devices:
        device["created_at"] = device["created_at"].replace(tzinfo=None)
        device["device_id"] = device["iccid"]
        combined_devices.append(device)


    combined_devices = sorted(combined_devices, key=lambda x: x["created_at"])

    return render(
        request,
        'devices.html',
        {'combined_devices': combined_devices}
    )

def device_details(request, id: str):
    ttn_devices = [device for device in ttn_cache if device['ids']['device_id'] == id]
    twilio_devices = [device for device in twilio_cache if device['iccid'] == id]

    if len(ttn_devices):
        device = ttn_devices[0]
        device_info = {
                'device_id': device['ids']['device_id'],
                'application_id': device['ids']['application_ids']['application_id'],
                'device_network': device['device_network'],
                'created_at': device['created_at'],
                'updated_at': device['updated_at'],
        }

        if device.get('ids').get('join_eui'):
            device_info["join_eui"] = device['ids']['join_eui']
        else:
            device_info["join_eui"] = "None"

        if device.get('ids').get('dev_eui'):
            device_info["dev_eui"] = device['ids']['dev_eui']
        else:
            device_info["dev_eui"] = "None"

        return render(
            request,
            'device_details.html',
            device_info
        )

    elif len(twilio_devices):
        device = twilio_devices[0]
        return render(
            request,
            'device_details.html',
            device
        )

    else:
        return render(
            request,
            'device_details.html',
            {'error': f'Device {id} not found.'}
        )

def twilio_view(request):
    # account_sid = request.GET.get('account_sid', False) # os.getenv('TWILIO_ACCOUNT_SID')
    # auth_token = request.GET.get('auth_token', False) # os.getenv('TWILIO_AUTH_TOKEN')
    load_dotenv()
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')

    try:
        client = Client(account_sid, auth_token)
    except TwilioException:
        return render(request, 'twilio.html', {'error': 'Invalid Twilio credentials.'})

    iccid = request.GET.get('iccid', False) # '89883070000004578983'
    registration_code = request.GET.get('registration_code', False) # 'XSTSYBZXQC'

    logger.debug(f"Account SID: {account_sid}")
    logger.debug(f"Auth token: {auth_token}")
    logger.debug(f"SIM ICCID: {iccid}")
    logger.debug(f"Registration code: {registration_code}")

    # try device registration
    try: 
        sim = client.supersim.v1.sims.create(iccid=iccid, registration_code=registration_code)
        logger.debug(f'Registed sim device with ssid "{sim.sid}"')
        return redirect("devices_view")
    except Exception:
        logger.warning(f'Failed to register sim device with iccid "{iccid}": {traceback.format_exc()}')
        if iccid and registration_code:
            return render(request, 'twilio.html',  {"error" : "Failed to register SIM device. Please make sure your device information is correct and that the device is not already registered."})
        return render(request, 'twilio.html')