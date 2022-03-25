from dataclasses import field
from unicodedata import category
from django.forms import ModelForm
from .models import Banner, Coupon, Product,Category
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ('category','product_name','description','price','size','stock','image1','image2','image3')

    # def clean(self):
    #     val_data = super(ProductForm,self).clean()
    #     description = val_data.get('description')
    #     if description == '':
    #         self.add_error('description','firld required')
        
    #     return val_data

        

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def catform(self):
        val_data = super(ProductForm,self).catform()
        cat_name = val_data.get('name')

        if cat_name != None:
            self.add_error('cat_name','Filed is required')
        return val_data

class CouponForm(ModelForm):
    class Meta:
        model = Coupon
        fields = ['code','discount','coupon_type','active']

class BannerForm(ModelForm):
    class Meta:
        model = Banner
        fields = '__all__'
    # def banner(self):
    #     val_data = super(BannerForm).add_error


