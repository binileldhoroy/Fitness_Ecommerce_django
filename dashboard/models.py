from asyncio import proactor_events
from re import T
from django.db import models
from fitness.models import User,ShippingAddress
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100,null=True)
    category_discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)],null=True,blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_name = models.CharField(max_length=100,null=True,unique=True)
    description = models.TextField(null=True)
    price = models.FloatField()
    size = models.CharField(max_length=50,null=True)
    image1 = models.ImageField(upload_to='images',null=True)
    image2 = models.ImageField(upload_to='images',null=True)
    image3 = models.ImageField(upload_to='images',null=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    stock = models.PositiveBigIntegerField(default=0,null=True)
    product_discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)],null=True)
    update = models.DateTimeField(auto_now=True,null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.product_name

    #if image url not fount
    @property
    def image1Url(self):
        try:
            url = self.image1.url
        except:
            url = ''
        return url

    @property
    def image2Url(self):
        try:
            url = self.image2.url
        except:
            url = ''
        return url

    @property
    def image3Url(self):
        try:
            url = self.image3.url
        except:
            url = ''
        return url

    #product and category discound
    @property
    def product_discount_price(self):
        cat = self.category.category_discount
        pro_dic = self.product_discount
        if pro_dic != '' and pro_dic != None  and cat != None and cat != '':
            if cat < pro_dic :
                price = self.price - (self.price * pro_dic / 100)
            else :
                price = self.price - (self.price * cat / 100)   
        elif pro_dic != '' and pro_dic != None :
            price = self.price - (self.price * pro_dic / 100)
        elif cat != None and cat != '':
            price = self.price - (self.price * cat / 100)
        else:
            price = self.price
        return round(price,2)
    

class Coupon(models.Model):
    types = (
        ('new','NEW'),
        ('ref','REF')
    )
    code = models.CharField(max_length=6,unique=True,null=True)
    valid_to = models.DateTimeField(null=True,blank=True)
    discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)])
    coupon_type = models.CharField(choices=types,null=True,max_length=10)
    active = models.BooleanField()

    def __str__(self):
        return self.code


class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    order_status = models.BooleanField(default=False)
    date_ordered = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(ShippingAddress,on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(null=True)
    approve_status = models.BooleanField(default=False)
    shipped_status = models.BooleanField(default=False)
    cancel_status = models.BooleanField(default=False)
    delivery_status = models.BooleanField(default=False)
    delivery_date = models.DateField(null=True)
    return_status = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True, blank=True)
    buy_now = models.BooleanField(default=False,null=True)

    class Meta:
        ordering = ('-date_ordered',)

    def __str__(self):
        return str(self.id)


    #total of cat products
    @property
    def get_cart_total(self):
        orderitem = self.orderitem_set.all()
        try:
            code = self.coupon.discount
        except:
            code = ''
        if code == '':
            total = sum([item.get_total for item in orderitem])
        else:
            total_dis = sum([item.get_total for item in orderitem])
            total = total_dis - (total_dis * code / 100)
        
        return round(total,2)
    
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
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order)

    @property
    def get_total(self):
        total = self.product.product_discount_price * self.quantity
        return total


class WishList(models.Model):
    wish_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    wish_product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return str(self.wish_product.id)


class Banner(models.Model):
    banner_title = models.CharField(max_length=100,null=True)
    banner_image = models.ImageField(upload_to='images',null=True,default='images/slider.svg')
    banner_description = models.CharField(max_length=100,null=True)
    active = models.BooleanField(default=True,null=True)

    @property
    def bannerImageUrl(self):
        try:
            url = self.banner_image.url
        except:
            url = ''
        return url
