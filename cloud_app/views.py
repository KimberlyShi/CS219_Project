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

from django.shortcuts import render
from django.http import HttpResponse
from .models import Devices

from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from dotenv import load_dotenv

logger = logging.getLogger('views')

TTN_POST_URL = 'https://symrec.eu1.cloud.thethings.industries/api/v3/applications/abctest/devices'

def home_view(request):
    return render(request, "home.html")

def ttn_view(request):
    # https://www.thethingsindustries.com/docs/the-things-stack/interact/api/#multi-step-actions

    load_dotenv()
    ttn_api_key = os.getenv('TTN_API_KEY')
    form_device_id = request.GET.get('device_id', False)
    form_device_eui = request.GET.get('device_eui', False)
    form_join_eui = request.GET.get('join_eui', False)

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
        return render(request, "ttn.html")
    try:
        r = requests.post(TTN_POST_URL, data=post_payload, headers=headers)
        resp_json = r.json()
        logger.debug('r.status_code', r.status_code)
        logger.debug('r.text', r.text)

        # output_status = r.text
        if r.status_code == 200:
            return devices_view(request)
        else:
            return render(
                request,
                "ttn.html",
                {"error": resp_json['details'][0]['message_format']}
            )

            # output_status = "Status: Device failed to register. Please make sure your device information is correct and that the device is not already registered."

    except Exception:
        logger.debug(f"Error: TTN Post.\n{traceback.format_exc()}")
        return render(request, "ttn.html", {"error": traceback.format_exc()})


def getTTNDevices():
    devices = subprocess.Popen(
        "ttn-lw-cli end-device list --application-id abctest", 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        shell=True
    )
    
    #converts returned bytes object into list of dicts
    output, _ = devices.communicate()
    dict_str = output.decode("UTF-8")
    devices_list = ast.literal_eval(dict_str) 

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
    ttn_devices = getTTNDevices()
    twilio_devices = getTwilioDevices()
    return render(
        request,
        'devices.html',
        {'ttn_devices': ttn_devices, 'twilio_devices': twilio_devices}
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
        return devices_view(request)
    except Exception:
        logger.warning(f'Failed to register sim device with iccid "{iccid}": {traceback.format_exc()}')
        return render(request, 'twilio.html',  {"output_status" : "Failed to register SIM device. Please make sure your device information is correct and that the device is not already registered."})