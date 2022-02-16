from django.db import models
from fitness.models import User,ShippingAddress

class Category(models.Model):
    name = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_name = models.CharField(max_length=100,null=True)
    description = models.TextField(null=True)
    price = models.FloatField()
    size = models.CharField(max_length=50,null=True)
    image1 = models.ImageField(upload_to='images',blank=True ,null=True)
    image2 = models.ImageField(upload_to='images',blank=True ,null=True)
    image3 = models.ImageField(upload_to='images',blank=True ,null=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    stock = models.PositiveBigIntegerField(default=0,null=True)
    update = models.DateTimeField(auto_now=True,null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.product_name


class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    order_status = models.BooleanField(default=False)
    date_ordered = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(ShippingAddress,on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitem = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitem])
        return total
    
    @property
    def get_cart_items(self):
        orderitem = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitem])
        return total


class Payment(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE, null=True)
    payment_method = models.CharField(max_length=50,null=True)
    payment_status = models.BooleanField(default=False,null=True)
    payment_amount = models.FloatField(null=True)

    def __str__(self):
        return str(self.payment_status)

class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.product)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total