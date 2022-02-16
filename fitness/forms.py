from dataclasses import fields
from urllib import request
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User,ShippingAddress

class MyUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','username','phone','email','password1','password2')

class AddressForm(ModelForm):
    class Meta:
        model = ShippingAddress
        fields = '__all__'
        exclude = ['user']