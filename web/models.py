from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.IntegerField
    email = models.EmailField
    name = models.TextField

class Devices(models.Model):
    device_id = models.IntegerField
    owning_user_id = models.IntegerField
    status = models.TextField

class Device_Model(models.Model):
    model_id = models.IntegerField
    model_name = models.TextField 
    image_url = models.URLField