from django.shortcuts import redirect, render
from django.contrib import messages
from .models import *
from .forms import *
from dashboard.models import Product
from dashboard.models import Order, OrderItem, Payment, Product
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.views.decorators.cache import never_cache   
from django.http import JsonResponse
from decouple import config
from datetime import datetime   
import random
import json
# Create your views here.

@never_cache
def loginView(request):
    page = 'login-page'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        uname = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=uname)
        except:
            messages.error(request,'User does not exits')
        if user.adminstatus == False:
            user = authenticate(request,username=uname,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                messages.error(request,'invalid username/password')
        else:
            messages.error(request,'You are blocked by Admin')
    
    return render(request,'fitness/login.html',{'page':page})

@never_cache
def otpLogin(request):
    global otp,number
    if request.method == 'POST':
        number = request.POST.get('mobnumber')
        try:
            user = User.objects.get(phone=number)
        except:
            messages.error(request,'Account does not exits with this number')

        otp = random.randrange(11111,99999)
        uname = user.first_name
        otp_body = str(uname) + ' ' + str(otp)

        account_sid = config('account_sid') 
        auth_token = config('auth_token') 
        client = Client(account_sid, auth_token)
        try:
            message = client.messages.create(  
                                  messaging_service_sid=config('messaging_service_sid'), 
                                  body= otp_body,
                                  from_='+19033296330',
                                  to='+91' + str(number)
                              ) 
        except TwilioRestException as e:
            messages.error(request,"Something went wrong " + repr(e.msg))

        return redirect('otp-verify')
    return render(request,'fitness/login.html')

@never_cache
def otpVerify(request):
    send_otp = otp
    print(send_otp)
    recv_number = number
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        if str(send_otp) == user_otp:
            try:
                user = User.objects.get(phone=recv_number)
            except:
                messages.error(request,'Account does not exits with this number')
            if user.adminstatus == False: 
                if user is not None:
                    login(request,user)
                    if request.user.is_authenticated:
                        print("authenticated")
                    return redirect('home')
                else:
                    messages.error(request,'invalid username/password')
            else:
                messages.error(request,'You are blocked by Admin')
        else:
            messages.error(request,'Incorrect OTP')

    return render(request,'fitness/otpverify.html')

@never_cache
def logoutView(request):
    logout(request)
    return redirect('home')

@never_cache
def signupView(request):
    form = MyUserForm()
    if request.method == 'POST':
        form = MyUserForm(request.POST)
        if form.is_valid():
            uphone = request.POST.get('phone')
            c_phone = User.objects.filter(phone=uphone)
            print(uphone)
            if uphone in c_phone:
                messages.error(request,'Account exists with this phone')
                return redirect('signup')
            else:
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                login(request,user)
                return redirect('home')
        else:
            messages.error(request,'SignUp Failed')
    context = {'form':form}
    return render(request,'fitness/signup.html',context)

@never_cache
def home(request):
    if request.user.is_authenticated:
        user = request.user
        order, created  = Order.objects.get_or_create(user = user,order_status=False)
        items = order.orderitem_set.all()
    else:
        order = []
    products = Product.objects.all()
    context = {'products':products,'order':order}
    return render(request,'fitness/home.html',context)

@never_cache
@login_required(login_url='login')
def myOrders(request):
    if request.user.is_authenticated:
        user = request.user
        order, created  = Order.objects.get_or_create(user = user,order_status=False)
        orders = Order.objects.filter(user=user,order_status=True)
        items = OrderItem.objects.all()
    context = {'orders':orders,'items':items,'order':order}
    return render(request,'fitness/myorders.html',context)


@never_cache
@login_required(login_url='login')
def productView(request,pk):
    if request.user.is_authenticated:
        user = request.user
        order, created  = Order.objects.get_or_create(user = user,order_status=False)
        items = order.orderitem_set.all()
    product = Product.objects.get(id=pk)
    related_product = Product.objects.filter(category=product.category)
    context = {'product':product,'re_products':related_product,'order':order}
    return render(request,'fitness/product.html',context)


@never_cache
@login_required(login_url='login')
def cart(request):
    if request.user.is_authenticated:
        user = request.user
        order, created  = Order.objects.get_or_create(user = user,order_status=False)
        items = order.orderitem_set.all()

    context = {'items':items,'order':order} 
    return render(request,'fitness/cart.html',context)


@never_cache
@login_required(login_url='login')
def updateCartItem(request):
    # data = json.loads(request.body)
    # productId = data['productId']
    # action = data['action']
    productId = request.POST.get('productId')
    action = request.POST.get('action')
    user = request.user
    product = Product.objects.get(id=productId)
    cur_stock = product.stock
    print('cur:-',cur_stock)
    order, created = Order.objects.get_or_create(user=user, order_status=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order,product=product)
    if cur_stock > orderItem.quantity:
        stock = 1
    else:
        stock = 0

    if action == 'add' and cur_stock > orderItem.quantity:
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

        if cur_stock > orderItem.quantity:
            stock = 1
        else:
            stock = 0

    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    response = {'items':order.get_cart_items,'quantity':orderItem.quantity,
    'total':orderItem.get_total,'cart_total':order.get_cart_total,'productId':productId,'stock':stock}
    return JsonResponse(response)


@never_cache
@login_required(login_url='login')
def checkOut(request):
    page = 'address'
    if request.user.is_authenticated:
        user = request.user
        order, created  = Order.objects.get_or_create(user = user,order_status=False)
        items = order.orderitem_set.all()
        address = user.shippingaddress_set.all()
        if request.method == 'POST':
            cur_address = request.POST.get('adrress')
            p_method = request.POST.get('payment')
            print(p_method)
            if cur_address == None or p_method == None:
                messages.error(request,'Select Address')
                return redirect('check-out')
            elif p_method == 'PayPal':
                messages.error(request,'PayPal Comming Soon please select COD')
                return redirect('check-out')
            else:
                cur_order = Order.objects.get(id=order.id)
                add = ShippingAddress.objects.get(id=cur_address)
                total = order.get_cart_total
                Payment(
                    order = cur_order,
                    payment_method = p_method,
                    payment_status = False,
                    payment_amount = total
                ).save()
                order.address = add
                now = datetime.now()
                cur_date = now.strftime("%d/%m/%Y %H:%M:%S")
                order.date = cur_date
                order.save()
                Order.objects.filter(user=user).update(order_status = True)
                items = order.orderitem_set.all()
                for item in items:
                    item_quantity = item.quantity
                    product_stock = item.product.stock
                    product_id = item.product.id
                    stock_updated = product_stock - item_quantity
                    Product.objects.filter(id = product_id).update(stock = stock_updated)
                return redirect('payment-complete')

        
    context = {'items':items,'order':order,'useraddress':address,'page':page}
    return render(request,'fitness/checkout.html',context)


@never_cache
@login_required(login_url='admin-login')
def orderCancel(request,pk):
    if request.user.is_authenticated:
        Order.objects.filter(id=pk).update(cancel_status=True)
        order = Order.objects.get(id=pk)
        items = order.orderitem_set.all()
        for item in items:
            item_quantity = item.quantity
            product_stock = item.product.stock
            product_id = item.product.id
            stock_updated = product_stock + item_quantity
            Product.objects.filter(id = product_id).update(stock = stock_updated)
            print(item_quantity)
            print('.....',product_stock)
            print(product_id)
            print('.....',stock_updated)
        return redirect('my-orders')
    else:
        messages.error(request,'Something went wrong')
        return render(request,'fitness/myorders.html')

    context = {'orders':order,'items':items,'order':order}
    return render(request,'fitness/myorders.html',context)

@never_cache
@login_required(login_url='login')
def changeAddress(request):
    form = AddressForm()
    if request.user.is_authenticated:
        user = request.user
        order, created  = Order.objects.get_or_create(user = user,order_status=False)
        items = order.orderitem_set.all()
        if request.method == 'POST':
            form = AddressForm(request.POST)
            if form.is_valid():
                address = form.save(commit=False)
                address.user = request.user
                address.save()
                return redirect('check-out')
    context = {'form':form,'items':items,'order':order}
    return render(request,'fitness/checkout.html',context)


@never_cache
@login_required(login_url='login')
def paymentComplete(request):
    return render(request,'fitness/paymentcomplete.html')