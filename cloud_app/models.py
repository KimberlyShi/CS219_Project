from django.db import models

# Create your models here.
class Devices(models.Model):
    d_id = models.CharField(max_length=200)
    network = models.CharField(max_length=200)
