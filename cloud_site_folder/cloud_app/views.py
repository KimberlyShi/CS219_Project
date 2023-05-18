from django.shortcuts import render

from django.http import HttpResponse

def home_view(request):
    # default GET
    # print(request.GET)
    # https://www.thethingsindustries.com/docs/the-things-stack/interact/api/#multi-step-actions
    return render(request, "home.html")

def ttn_view(request):
    return render(request, "ttn.html")

def index(request):
    return HttpResponse("Hello World")
