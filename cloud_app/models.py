from django.db import models

# Create your models here.
class Devices(models.Model):
    d_id = models.CharField(max_length=200)
    network = models.CharField(max_length=200)

# Stores mappings for devices and their unique IDs
class DeviceUIDS(models.Model):
    u_name = models.CharField(unique=True, max_length=200)
    uid = models.AutoField(primary_key=True)
