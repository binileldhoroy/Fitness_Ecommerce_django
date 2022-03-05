from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import generateRefCode

# Create your models here.

class User(AbstractUser):
    phone = models.BigIntegerField(null=True,unique=True)
    adminstatus = models.BooleanField(blank=True,default=False,null=True)
    biopic = models.ImageField(upload_to='images',null=True,default='images/avater.svg')


class Referral(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=12,blank=True,null=True)
    recommended_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name='ref_by')
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}-{self.ref_code}'

    def getRecommenedProfiles(self):
        pass

    def save(self, *args, **kwargs):
        if self.ref_code == '' or self.ref_code == None:
            ref_code = generateRefCode()
            self.ref_code = ref_code
        super().save(*args,**kwargs)

class ShippingAddress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    f_name = models.CharField(max_length=200, null=True)
    l_name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    phone = models.BigIntegerField(null=True)
    address1 = models.CharField(max_length=200, null=True)
    address2 = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    pincode = models.CharField(max_length=200, null=True)
    post_office = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)