from django.shortcuts import render

from django.http import HttpResponse

def home_view(request):
    # default GET
    # print(request.GET)
    return render(request, "home.html")

def index(request):
    return HttpResponse("Hello World")
