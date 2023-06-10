from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name="home_view"),
    path('ttn/', views.ttn_view, name="ttn_view"),
    # path('ttn_submit/', views.ttn_submit, name="ttn_submit"),
    path('devices/', views.devices_view, name="devices_view"),
    path('twilio/', views.twilio_view, name="twilio_view"),

    # path('', views.index, name='index'),
]