from dataclasses import field
from django.forms import ModelForm
from .models import Banner, Coupon, Product,Category
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['category','product_name','description','price','size','stock','image1','image2','image3']

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class CouponForm(ModelForm):
    class Meta:
        model = Coupon
        fields = ['code','discount','coupon_type','active']

class BannerForm(ModelForm):
    class Meta:
        model = Banner
        fields = '__all__'


