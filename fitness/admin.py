from django.contrib import admin

from dashboard.models import WishList
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(ShippingAddress)
admin.site.register(Referral)
admin.site.register(WishList)
