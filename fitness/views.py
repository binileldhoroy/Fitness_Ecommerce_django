import json
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import *
from .forms import *
from dashboard.models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from datetime import datetime 
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView
from .otp import *
from django.template.loader import render_to_string
from django.db.models import Q, Min, Max
from .cookie_cart import cookieCart

# Create your views here.

@never_cache
def loginView(request):
    page = 'login-page'
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        not_active = User.objects.filter(is_active=False)
        not_active.delete()
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
                return redirect('index')
            else:
                messages.error(request,'invalid username/password')
        else:
            messages.error(request,'You are blocked by Admin')
    
    return render(request,'fitness/login.html',{'page':page})

@never_cache
def otpLogin(request):
    global phone
    if request.method == 'POST':
        phone = request.POST.get('mobnumber')
        number = '+91' + str(phone)
        user = None
        
        try:
            user = User.objects.get(phone=phone)
        except:
            
            messages.error(request,"There is no user with this phone number")
            return render(request, 'fitness/login.html',)
        if user is not None:
            try:
                status = otp_login_code(request,number)
            except TwilioRestException as e:
                messages.error(request,e)
            return redirect('otp-verify')
    return render(request, 'fitness/login.html')


@never_cache
def otpVerify(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if len(str(otp)) < 4 or len(str(otp)) > 10 :
            messages.error(request,"Invalid Entry")
        else:
            user = User.objects.get(phone= phone)
            username = user.username
            number = '+91' + str(phone)
            try:
                status = None
                status = otp_verify_code(request,number,otp)
            except TwilioRestException as e:
                messages.error(request,e)
            if status == 'approved':
                if user.adminstatus == False :
                    login(request,user)
                   
                    return redirect('index')
                else:
                    messages.error(request,"You seems blocked try again later")
            else:
                
                messages.error(request,"Incorrect OTP ")
                return render(request, 'fitness/otpverify.html')
    else :
        messages.success(request,"OTP has been sent")
    return render(request,'fitness/otpverify.html')



@never_cache
def logoutView(request):
    logout(request)
    return redirect('index')

@never_cache
def signupView(request, *args, **kwargs):
    not_active = User.objects.filter(is_active=False)
    not_active.delete()
    form = MyUserForm()
    code = kwargs.get('ref_code')
    try:
        profile = Referral.objects.get(ref_code=code)
        request.session['ref_profile'] = profile.user.id
    except:
        pass
    if request.method == 'POST':
        try:
            profile_id = request.session.pop('ref_profile')
        except:
            profile_id = None
        form = MyUserForm(request.POST)
        if form.is_valid():
            if profile_id is not None:
                recommended_by_profile = User.objects.get(id=profile_id)
                uphone = request.POST.get('phone')
                username = request.POST.get('username')
                phone_number = '+91' + str(uphone)
                c_phone = User.objects.filter(phone=uphone)
                if uphone in c_phone:
                    messages.error(request,'Account exists with this phone')
                    return redirect('signup')
                else:
                    request.session['phone_number'] = phone_number
                    user = form.save(commit=False)
                    user.is_active = False
                    user.username = user.username.lower()
                    user.save()
                    
                    reg_user = User.objects.get(username=username)
                    user_ref = Referral.objects.get(user=reg_user)
                    user_ref.recommended_by = recommended_by_profile
                    user_ref.save()
                    try:
                        status = otp_login_code(request,phone_number)
                        return redirect('otp-verify-signup')
                    except TwilioRestException as e:
                        messages.error(request,e)
                    
            else:
                uphone = request.POST.get('phone')
                request.session['phone_number'] = uphone
                phone_number = '+91' + str(uphone)
                c_phone = User.objects.filter(phone=uphone)
                if uphone in c_phone:
                    messages.error(request,'Account exists with this phone')
                    return redirect('signup')
                else:
                    user = form.save(commit=False)
                    user.is_active = False
                    user.username = user.username.lower()
                    user.save()
                    try:
                        status = otp_login_code(request,phone_number)
                        return redirect('otp-verify-signup')
                    except TwilioRestException as e:
                        messages.error(request,e)
        else:
            messages.error(request,'SignUp failed try again')
    context = {'form':form}
    return render(request,'fitness/signup.html',context)


@never_cache
def otpVerifySignUp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if len(str(otp)) < 4 or len(str(otp)) > 10 :
            messages.error(request,"Invalid Entry")
        else:
            try:
                phone_number = request.session.pop('phone_number')
            except:
                messages.error(request,'SignUp Faild try again')
                return redirect('signup')
            
            number = '+91' + str(phone_number)
            try:
                status = None
                status = otp_verify_code(request,number,otp)
            except TwilioRestException as e:
                messages.error(request,e)
            if status == 'approved':
                try:
                    user = User.objects.get(phone= phone_number)
                except:
                    messages.error(request,'SignUp failed Try again')
                    return redirect('index')
                user.is_active = True
                user.save()
                login(request,user)
                return redirect('index')
            else:
                
                messages.error(request,"Incorrect OTP ")
                return render(request, 'fitness/otp_verify_signup.html')
    else :
        messages.success(request,"OTP has been sent")
    return render(request,'fitness/otp_verify_signup.html')


@never_cache
def home(request):
    # q = request.GET.get('q') if request.GET.get('q') != None else ''
    if request.method == 'GET':
        q = request.GET.get('q')
        min_price = request.GET.get('minprice')
        max_price = request.GET.get('maxprice')
        if q == None:
            q = ''
    cart_item = False
    user = request.user
    try:
        wish = [i.wish_product for i in  WishList.objects.filter(wish_user=user)]
    except:
        wish=''
    if request.user.is_authenticated:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        
        if bool(cart):
            order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
            for i in cart:
                product = Product.objects.get(id=i)
                try:
                    item = OrderItem.objects.get(product=product, order=order)
                except:
                    item = OrderItem.objects.create(product=product,order=order,quantity=0)
                quantity = int(item.quantity) + cart[i]['quantity']
                OrderItem.objects.filter(product=product, order=order).update(quantity=quantity)
                cart_item = True
        else:
            order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
        
    else:
        cookieData = cookieCart(request)
        order = cookieData['order']
    
    cats = Category.objects.all()
    minPrice = Product.objects.aggregate(Min('price'))
    maxPrice = Product.objects.aggregate(Max('price'))
    if max_price != None and min_price != None:
        products = Product.objects.filter(price__range=(min_price, max_price))
    else:    
        products = Product.objects.filter(
            Q(product_name__icontains=q)|
            Q(description__icontains=q)|
            Q(category__name__icontains=q)
        )
    context = {'products':products,
            'cats':cats,'cart_item':cart_item,
            'order':order,'wish':wish,'minPrice':minPrice,
            'maxPrice':maxPrice
            }
    return render(request,'fitness/home.html',context)


def index(request):
    cart_item = False
    user = request.user
    try:
        wish = [i.wish_product for i in  WishList.objects.filter(wish_user=user)]
    except:
        wish=''
    if request.user.is_authenticated:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        
        if bool(cart):
            order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
            for i in cart:
                product = Product.objects.get(id=i)
                try:
                    item = OrderItem.objects.get(product=product, order=order)
                except:
                    item = OrderItem.objects.create(product=product,order=order,quantity=0)
                quantity = int(item.quantity) + cart[i]['quantity']
                OrderItem.objects.filter(product=product, order=order).update(quantity=quantity)
                cart_item = True
        else:
            order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
        
    else:
        cookieData = cookieCart(request)
        order = cookieData['order']
    
       
    products = Product.objects.all().order_by('-id')[:4]
    banners = Banner.objects.all().order_by('id')
    context = {'products':products,
            'cart_item':cart_item,'banners':banners,
            'order':order,'wish':wish
            }
    return render(request,'fitness/index.html',context)


def filterData(request):
    category = request.GET.getlist('category[]')
    products  = Product.objects.all().order_by('-id').distinct()
    minPrice = request.GET['minPrice']
    maxPrice  = request.GET['maxPrice']
    # products = products.filter(price__lte=minPrice)
    products = products.filter(price__gte=maxPrice)
    
    if len(category) > 0:
        products = products.filter(category__id__in=category).distinct()
    t = render_to_string('fitness/product-list.html',{'products':products})
    return JsonResponse({'data':t})


@never_cache
@login_required(login_url='login')
def myOrders(request):
    if request.user.is_authenticated:
        user = request.user
        order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
        orders = Order.objects.filter(user=user,order_status=True)
        items = OrderItem.objects.all()
    context = {'orders':orders,'items':items,'order':order}
    return render(request,'fitness/myorders.html',context)


@never_cache
def productView(request,pk):
    if request.user.is_authenticated:
        user = request.user
        order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        order = cookieData['order']
    product = Product.objects.get(id=pk)
    related_product = Product.objects.filter(category=product.category)
    context = {'product':product,'re_products':related_product,'order':order}
    return render(request,'fitness/product.html',context)


@never_cache
def cart(request):
    if request.user.is_authenticated:
        user = request.user
        Order.objects.filter(user = user,order_status=False,buy_now=True).delete()
        order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
        items = order.orderitem_set.all()
    else:
        cookieData = cookieCart(request)
        order = cookieData['order']
        items = cookieData['items']

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
    order, created = Order.objects.get_or_create(user=user, order_status=False,buy_now=False)

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
def buyNow(request,pk):
    if request.user.is_authenticated:
        user = request.user
        Order.objects.filter(user = user,order_status=False,buy_now=True).delete()
        order = Order.objects.create(user = user,order_status=False,buy_now=True)
        product = Product.objects.get(id = pk)
        orderItem = OrderItem.objects.create(order=order,product=product,quantity=1)
        return redirect('check-out')



@never_cache
@login_required(login_url='login')
def checkOut(request):
    page = 'address'
    if request.user.is_authenticated:
        user = request.user
        # breakpoint()
        try:
            order = Order.objects.get(user = user,order_status=False,buy_now=True)
        except:
            order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
        items = order.orderitem_set.all()
        coupon = Coupon.objects.all()
        ref = Referral.objects.get(user=user)
        ref_count = Referral.objects.filter(user=user).count()
        try:
            ref_user = ref.recommended_by
            if ref_user is None:
                ref_user = ''
        except:
            ref_user = ''
        print(ref_user)
        address = user.shippingaddress_set.all()
        if request.method == 'POST':
            cur_address = request.POST.get('adrress')
            # p_method = request.POST.get('payment')
            # print(p_method)

            # if p_method == 'cod':
            #     p_status = False
            # elif p_method == 'paypal':
            #     p_status = True

            if cur_address == None:
                messages.error(request,'Select Address')
                return redirect('check-out')
            else:
                cur_order = Order.objects.get(id=order.id)
                add = ShippingAddress.objects.get(id=cur_address)
                total = order.get_cart_total
                Payment(
                    order = cur_order,
                    payment_method = 'cod',
                    payment_status = False,
                    payment_amount = round(total,2)
                ).save()
                order.address = add
                now = datetime.now()
                cur_date = now
                order.date = cur_date
                order.save()
                Order.objects.filter(id=order.id).update(order_status = True)
                items = order.orderitem_set.all()
                for item in items:
                    item_quantity = item.quantity
                    product_stock = item.product.stock
                    product_id = item.product.id
                    stock_updated = product_stock - item_quantity
                    Product.objects.filter(id = product_id).update(stock = stock_updated)
                data = {'status':'Your order has placed successfully'}
                return JsonResponse(data)

        
    context = {'items':items,'order':order,'useraddress':address,'page':page,'coupons':coupon,'ref_user':ref_user,'ref_count':ref_count}
    return render(request,'fitness/checkout.html',context)


@never_cache
@login_required(login_url='login')
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
        return redirect('my-orders')
    else:
        messages.error(request,'Something went wrong')
        return render(request,'fitness/myorders.html')

    context = {'orders':order,'items':items,'order':order}
    return render(request,'fitness/myorders.html',context)

@never_cache
@login_required(login_url='login')
def paymentComplete(request):
    return render(request,'fitness/paymentcomplete.html')


@never_cache
@login_required(login_url='login')
def payRazorpay(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            order = Order.objects.get(user = user,order_status=False,buy_now=True)
        except:
            order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
        cur_order = Order.objects.get(id = order.id)
        cart_total = order.get_cart_total
        full_name = user.first_name + user.last_name
        email = user.email
        phone = user.phone
        return JsonResponse({
        'cart_total':round(cart_total,2),
        'full_name':full_name,
        'email':email,
        'phone':phone
        })


@never_cache
@login_required(login_url='login')
def razorpayComplete(request):
    if request.user.is_authenticated:
        user = request.user

        try:
            order = Order.objects.get(user = user,order_status=False,buy_now=True)
        except:
            order, created  = Order.objects.get_or_create(user = user,order_status=False,buy_now=False)
        items = order.orderitem_set.all()

        cur_address = request.POST.get('cur_address')
        # p_method = request.POST.get('payment')
        # print(p_method)
        address = user.shippingaddress_set.all()
        cur_order = Order.objects.get(id=order.id)
        add = ShippingAddress.objects.get(id=cur_address)
        total = order.get_cart_total

        Payment(
            order = cur_order,
            payment_method = 'razorpay',
            payment_status = True,
            payment_amount = round(total,2)
        ).save()

        order.address = add
        now = datetime.now()
        cur_date = now
        order.date = cur_date
        order.save()
        Order.objects.filter(id=order.id).update(order_status = True)
        items = order.orderitem_set.all()
        for item in items:
            item_quantity = item.quantity
            product_stock = item.product.stock
            product_id = item.product.id
            stock_updated = product_stock - item_quantity
            Product.objects.filter(id = product_id).update(stock = stock_updated)
    
        return JsonResponse({'status':'Your order has placed successfully'}) 


@never_cache
@login_required(login_url='login')
def myProfile(request):
    user = request.user
    referral = Referral.objects.get(user=user)
    order = Order.objects.get(user = user,order_status=False)
    counts = WishList.objects.filter(wish_user=user).count()
    return render(request,'fitness/myprofile.html',{'referral':referral,'order':order,'counts':counts})


@never_cache
@login_required(login_url='login')
def myAddress(request):
    if request.user.is_authenticated:
        form = AddressForm()
        user = request.user
        address = user.shippingaddress_set.all()
        order = Order.objects.get(user = user,order_status=False)
        counts = WishList.objects.filter(wish_user=user).count()
        if request.method == 'POST':
            ShippingAddress.objects.create(
                user = request.user,
                f_name = request.POST.get('firstname'),
                l_name = request.POST.get('lastname'),
                email = request.POST.get('email'),
                phone = request.POST.get('phone'),
                address1 = request.POST.get('address1'),
                address2 = request.POST.get('address2'),
                city = request.POST.get('city'),
                state = request.POST.get('state'),
                pincode = request.POST.get('pin'),
                post_office = request.POST.get('office')
                )
            return redirect('my-address')

        context = {'form':form,'useraddress':address,'order':order,'counts':counts}
        return render(request,'fitness/myaddress.html',context)


@never_cache
@login_required(login_url='admin-login')
def deleteAddress(request,pk):
    if request.user.is_authenticated:
        address = ShippingAddress.objects.get(id=pk)
        if request.method == 'POST':
            address.delete()
            return redirect('my-address')
    return render(request,'fitness/delete.html')



@never_cache
@login_required(login_url='login')
def changeAddress(request,pk):
     if request.user.is_authenticated:
        address = ShippingAddress.objects.get(id=pk)
        form = AddressForm(instance=address)
        
        order = Order.objects.get(user = request.user,order_status=False)
        if request.method == 'POST':
            form = AddressForm(request.POST,instance=address)
            if form.is_valid():
                form.save()
                messages.success(request,'Update Successfully')
            return redirect('my-address')
                
        context = {'form':form,'order':order}
        return render(request,'fitness/edit_address.html',context)


@never_cache
@login_required(login_url='login')
def editProfile(request):
    user = request.user
    form = EditProfileForm(instance=user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('my-profile')
    return render(request,'fitness/edit_profile.html',{'form':form})

class MyPasswordChangeView(PasswordChangeView):
    template_name = 'fitness/change_password.html'
    success_url = reverse_lazy('change-password-done')
    def get_context_data(self,*args, **kwargs):
        context = super( MyPasswordChangeView, self).get_context_data(*args,**kwargs)
        user = self.request.user
        context['counts'] = WishList.objects.filter(wish_user=user).count()
        return context

class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'fitness/password_reset_done.html'



@never_cache
@login_required(login_url='login')
def applyCoupon(request):
    
    code = request.POST.get('copoun')
    try:
        code = Coupon.objects.get(code = code)
        user = request.user
        order = Order.objects.filter(user = user,coupon = code).exists()
        if order == False:
            if request.method == 'POST':
                Order.objects.filter(user = user,order_status=False).update(coupon = code)  
        else:
            messages.error(request,'Coupon Already Applyed')
    except:
        messages.error(request,'Invalid Coupon')
    return redirect('check-out')


@never_cache
@login_required(login_url='login')
def removeCoupon(request,pk):
    user = request.user
    Order.objects.filter(user = user,order_status=False,id = pk).update(coupon = '')
    return redirect('check-out')


def addWishList(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            productId = request.POST.get('wish_product')
            action = request.POST.get('wish_action')
            product = Product.objects.get(id=productId)
            if action == 'add_wish':
                wishlist = WishList.objects.get_or_create(wish_user=user,wish_product=product)
                result = 'added'
                status = 'added to'
            elif action == 'remove_wish':
                wishlist = WishList.objects.get(wish_user=user,wish_product=product)
                wishlist.delete()
                result = 'removed'
                status = 'removed from'
        data = {'result':result,'productId':productId,'status':status}
    return JsonResponse(data)


def myWishList(request):
    user = request.user
    products = WishList.objects.filter(wish_user=user)
    counts = products.count()
    wish = [i.wish_product for i in  WishList.objects.filter(wish_user=user)]
    return render(request,'fitness/mywishlist.html',{'products':products,'wish':wish,'counts':counts})