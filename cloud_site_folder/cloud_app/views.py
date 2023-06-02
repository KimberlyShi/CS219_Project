from django.shortcuts import render

from django.http import HttpResponse

from .models import Devices

import requests, json

import os
from twilio.rest import Client
from dotenv import load_dotenv

def home_view(request):
    return render(request, "home.html")

def ttn_view(request):
    # https://www.thethingsindustries.com/docs/the-things-stack/interact/api/#multi-step-actions
    request_params = {
        "device_id": request.GET.get('device_id', False),
        "dev_eui": request.GET.get('device_eui', False),
        "join_eui": request.GET.get('join_eui', False),
        # "join_server_address": request.GET['join_server_address'],
    }

    # To register a device newdev1 in application app1, first, register the DevEUI, JoinEUI and cluster addresses in the Identity Server. 
    data = {
        "end_device": {
            "ids": request_params,
            "join_server_address": "thethings.example.com",
            "network_server_address": "thethings.example.com",
            "application_server_address": "thethings.example.com"
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
            'https://thethings.example.com/api/v3/applications/app1/devices', 
            data=post_payload)
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
        sim = client.supersim.v1.sims.create(iccid='89883070000123456789', registration_code='H3LL0W0RLD')
        print(sim.sid)
    except:
        print("bad user or token")
    return render(request, "twilio.html")
