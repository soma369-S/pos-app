from django.db import models
class Device(models.Model):
    imei=models.CharField(max_length=50,unique=True)
