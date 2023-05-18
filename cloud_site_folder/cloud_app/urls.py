from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name="home_view"),
    path('ttn/', views.ttn_view, name="ttn_view"),
    # path('', views.index, name='index'),
]