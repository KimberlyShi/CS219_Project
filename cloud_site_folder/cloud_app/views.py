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
#     ttn_status = "ok"
#     return render(request, "ttn.html", {'ttn_status': ttn_status})

def ttn_view(request):
    # https://www.thethingsindustries.com/docs/the-things-stack/interact/api/#multi-step-actions
    request_params = {
        "device_id": request.GET.get('device_id', False),
        "dev_eui": request.GET.get('device_eui', False),
        "join_eui": request.GET.get('join_eui', False),
        # "join_server_address": request.GET['join_server_address'],
    }

    # To register a device newdev1 in application app1, first, register the DevEUI, JoinEUI and cluster addresses in the Identity Server. 
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer NNSXS.V2E6Z34WKY7OWEKMBNCHWZMV5PPEDNT7ZNEXLBY.3OHCZN4WUOUSN2ZXB6NP54R6E7ANC7HJIDVD6YIIFNIFYVU3AFSQ',
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

    try:
        r = requests.post(
            'https://symrec.eu1.cloud.thethings.industries/api/v3/applications/abctest/devices', 
            data=post_payload, headers=headers)
    except requests.exceptions.RequestException as e:
        # raise SystemExit(e)
        print("Error: TTN Post")

    return render(request, "ttn.html")

def index(request):
    return HttpResponse("Hello World")



def devices_view(request):
    print(Devices.objects.all())
    return render(request, 'devices.html', {'device': Devices.objects.all()})

def twilio_view(request):
    return render(request, "twilio.html")

def register_device(request):
    load_dotenv()
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    try:
        # sim = client.supersim.v1.sims.create(iccid='89883070000004578975', registration_code='H3LL0W0RLD')
        # print("registered device: ")
        # print(sim.sid)
        sim = client.supersim.v1.sims('HS292982d1e4647acb2966c69425e06be3').fetch()
        print("status:", sim.status)
        print("fleet:", sim.fleet)
    except Exception as e: 
        print("exception: ")
        print(e)
    return render(request, "twilio.html")
