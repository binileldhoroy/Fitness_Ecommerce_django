from dataclasses import fields
from pyexpat import model
from urllib import request
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User,ShippingAddress
from django.core.exceptions import ValidationError


class MyUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','username','phone','email','password1','password2')

    def clean(self):
        val_data = super(MyUserForm,self).clean()
        first_name = val_data.get('first_name')
        last_name = val_data.get('last_name')
        username = val_data.get('username')
        phone = val_data.get('phone')
        email = val_data.get('email')
        password1 = val_data.get('password1')
        password2 = val_data.get('password2')

        if username != None and len(username) < 5:
            self.add_error('username', "Username must have 5 letters")
        if password1 != password2:
            self.add_error('password2', "Password does not match")
        if first_name == "":
            self.add_error('first_name', "This field is required")
        if last_name == "":
            self.add_error('last_name', "This field is required")
        if User.objects.filter(username=username).exists():
            a = User.objects.get(username=username)
        if email == '':
            self.add_error('email', "This field is required")

        if phone and len(str(phone)) < 10:
            self.add_error('phone', "minimum length is 10")
        elif phone and len(str(phone)) > 10:
            self.add_error('phone', "maximum legth is 10")
    
        return val_data
            

class AddressForm(ModelForm):
    class Meta:
        model = ShippingAddress
        fields = '__all__'
        exclude = ['user']


class EditProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','biopic']
   