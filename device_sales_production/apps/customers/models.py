from django.db import models
class Customer(models.Model):
    full_name=models.CharField(max_length=200)
