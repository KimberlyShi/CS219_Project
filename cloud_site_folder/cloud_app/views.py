from django.shortcuts import render

from django.http import HttpResponse

from .models import Devices

import requests, json

import os
from twilio.rest import Client
from dotenv import load_dotenv

def home_view(request):
    return render(request, "home.html")

# def ttn_view(request):
#     # ttn_status = "ok"
#     return render(request, "ttn.html")

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
    
    if(form_device_id and form_device_eui and form_join_eui):
        try:
            r = requests.post(
                'https://symrec.eu1.cloud.thethings.industries/api/v3/applications/abctest/devices', 
                data=post_payload, headers=headers)
            print(r)
        # except requests.exceptions.RequestException as e:
        except Exception as e:
            # raise SystemExit(e)
            print("Error: TTN Post")
    else:
        print("Form not completed yet")

    return render(request, "ttn.html")

def index(request):
    return HttpResponse("Hello World")



def devices_view(request):
    print(Devices.objects.all())
    return render(request, 'devices.html', {'device': Devices.objects.all()})

def twilio_view(request):
    # account_sid = request.GET.get('account_sid', False) # os.getenv('TWILIO_ACCOUNT_SID')
    # auth_token = request.GET.get('auth_token', False) # os.getenv('TWILIO_AUTH_TOKEN')
    load_dotenv()
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')    
    client = Client(account_sid, auth_token)

    iccid = request.GET.get('iccid', False) # '89883070000004578983'
    registration_code = request.GET.get('registration_code', False) # 'XSTSYBZXQC'
    debug = True
    if debug:
        print("account_sid: ", account_sid)
        print("auth_token: ", auth_token)
        print("iccid: ", iccid)
        print("registration_code: ", registration_code)
    output_json = None
    data = {}
    data["devices"] = []
    # try device registration
    try: 
        sim = client.supersim.v1.sims.create(iccid=iccid, registration_code=registration_code)
        print("registered device: ")
        print(sim.sid)
    except Exception as e:
        print("exception for device registration: ", e)

    # api call to retrieve devices on twilio
    try:
        sid = "HS292982d1e4647acb2966c69425e06be3"
        sim = client.supersim.v1.sims(sid).fetch()
        data["devices"].append({"sid": sid, "status": sim.status})
        print("status:", sim.status)
        # print("fleet:", sim.fleet)
        output_json = json.dumps(data)
        print("data: ", data)
        print("json: ", output_json)
    except Exception as e: 
        print("exception: ")
        print(e)
    return render(request, 'twilio.html',  {"data" : output_json} )

