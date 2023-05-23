from django.shortcuts import render

from django.http import HttpResponse

import requests, json

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
    return HttpResponse("Hello World")

