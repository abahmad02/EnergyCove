from django.db import models
from datetime import datetime
# Create your models here.
class Panel(models.Model):
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    power = models.DecimalField(max_digits=10, decimal_places=2)
    default_choice = models.BooleanField(default=False)
    availability = models.BooleanField(default=True)
    
class Inverter(models.Model):
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    power = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)

class variableCosts(models.Model):
    cost_name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    
class PotentialCustomers(models.Model):
    name = models.CharField(max_length=15)
    phone = models.CharField(max_length=11)
    address = models.TextField()
    reference_number = models.CharField(max_length=14)
    date = models.DateTimeField(default=datetime.now)

class BracketCosts(models.Model):
    Type = models.CharField(max_length=15)
    SystemRange = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)