from django.shortcuts import render

from django.http import HttpResponse

from .models import Devices

import requests, json, subprocess, ast

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




def getTTNDevices():
    # print(os.system("ttn-lw-cli use symrec.nam1.cloud.thethings.industries"))
    # print(os.system("ttn-lw-cli login --callback=false"))
    devices = subprocess.Popen("ttn-lw-cli end-device list --application-id abctest", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, _ = devices.communicate()
    dict_str = output.decode("UTF-8")
    devices_list = ast.literal_eval(dict_str)
    for device in devices_list:
        device["device_network"] = "TTN"
    return devices_list



def devices_view(request):
    ttn_devices = getTTNDevices()
    # return render(request, 'devices.html', {'devices': Devices.objects.all()})
    return render(request, 'devices.html', {'devices': ttn_devices})
