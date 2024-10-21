
from django.db import models


class Oil_Companies(models.Model):
    name = models.CharField(max_length=200,null=True,blank=True)    
    
    def __str__(self):
        return self.name
    
    
    
class NewEntry(models.Model):
    name = models.CharField(max_length=200,null=True,blank=True)
    phone_number = models.CharField(max_length=100,null=True,blank=True)
    vehicle =  models.CharField(max_length=300,null=True,blank=True)
    registeration_num = models.CharField(max_length=300,null=True,blank=True)
    date = models.DateField()
    last_reading = models.CharField(max_length=500,null=True,blank=True)
    next_reading = models.CharField(max_length=500,null=True,blank=True)
    next_changing_date = models.DateField()
    oil_companies = models.ForeignKey(Oil_Companies,on_delete=models.CASCADE,null=True,blank=True)
    oil_quantity = models.CharField(max_length=500,null=True,blank=True)
    oil_price = models.CharField(max_length=500,null=True,blank=True)
    oil_filter = models.CharField(max_length=500,null=True,blank=True)
    ac_filter = models.CharField(max_length=500,null=True,blank=True)
    air_filter = models.CharField(max_length=500,null=True,blank=True)
    
    
    
    def __str__(self):
        return self.name + ' ' + self.phone_number + ' ' + self.vehicle + ' ' + self.registeration_num

