from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Product,Category
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['category','product_name','description','price','size','stock','image1','image2','image3']

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


