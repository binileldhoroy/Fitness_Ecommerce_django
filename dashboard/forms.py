from dataclasses import field
from django.forms import ModelForm
from .models import Coupon, Product,Category
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['category','product_name','description','price','size','stock','product_discount','image1','image2','image3']

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class CouponForm(ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'


