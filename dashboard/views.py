from multiprocessing import context
from django.shortcuts import redirect, render
from fitness.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import ProductForm,CategoryForm
from .models import *

# Create your views here.
@never_cache
def adminLogin(request):
    if request.user.is_authenticated:
        if request.user.username == 'binil':
            return redirect('admin-home')
        else:
            return redirect('login')
    if request.method == 'POST':
        admin = request.POST.get('admin')
        password = request.POST.get('password')
        if admin == 'binil' and password == 'asdfghjkl':
            try:
                user = User.objects.get(username=admin)
            except:
                messages.error(request,'User does not exits')
            user = authenticate(request,username=admin,password=password)
            if user is not None:
                login(request,user)
                return redirect('admin-home')
            else:
                messages.error(request,'You are not Admin')
        else:
            messages.error(request,'Invalid username/password')
    return render(request,'dashboard/dash_login.html')

@never_cache
def adminLogout(request):
    logout(request)
    return redirect('admin-login')

@never_cache
@login_required(login_url='admin-login')
def adminHome(request):
    if request.user.username == 'binil':
        return render(request,'dashboard/dash_home.html')
    else:
        return redirect('login')
        

@never_cache
@login_required(login_url='admin-login')
def viewUser(request):
    if request.user.username == 'binil':
        users = User.objects.all()
        context = {'users':users}
        return render(request,'dashboard/view_user.html',context)
    else:
        return redirect('login')
    


@never_cache
@login_required(login_url='admin-login')
def blockUser(request,pk):
    user = User.objects.get(id=pk)
    if user.adminstatus == False:
        User.objects.filter(id=pk).update(adminstatus=True)
        return redirect('user-view')
    else:
        User.objects.filter(id=pk).update(adminstatus=False)
        return redirect('user-view')

@never_cache
@login_required(login_url='admin-login')
def addProduct(request):
    page = 'add-product'
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'Product is Added')
            return redirect('add-product')
    else:
        return render(request,'dashboard/dash_addproduct.html',{'form':form,'page':page})

@never_cache
@login_required(login_url='admin-login')
def viewProduct(request):
    products = Product.objects.all()
    return render(request,'dashboard/view_product.html',{'products':products})


@never_cache
@login_required(login_url='admin-login')
def editProduct(request,pk):
    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST,instance=product)
        if form.is_valid():
            form.save()
            messages.success(request,'Update Successfully')
            return redirect('view-product')
    return render(request,'dashboard/edit_product.html',{'form':form})


@never_cache
@login_required(login_url='admin-login')
def deleteProduct(request,pk):
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('view-product')
    return render(request,'dashboard/delete_product.html')

@never_cache
@login_required(login_url='admin-login')
def addCategory(request):
    form = CategoryForm()
    if request.method == 'POST':
        category = request.POST.get('name')
        Category.objects.get_or_create(name=category)
        messages.success(request,'Cateory is Added')
        return redirect('add-category')
    else:
        return render(request,'dashboard/dash_addproduct.html',{'form':form})



@never_cache
@login_required(login_url='admin-login')
def viewOrders(request):
    if request.user.is_authenticated:
        orders = Order.objects.all().filter(order_status=True)
    else:
        messages.error(request,'Empty Orders')
        return render(request,'dashboard/view_orders.html')
    context = {'orders':orders}    

    return render(request,'dashboard/view_orders.html',context)


@never_cache
@login_required(login_url='admin-login')
def orderItemView(request,pk):
    if request.user.is_authenticated:
        order = Order.objects.get(id=pk)
        items = order.orderitem_set.all()
    else:
        messages.error(request,'Something went wrong')
        return render(request,'dashboard/view_items.html')
    context = {'order':order,'items':items}    

    return render(request,'dashboard/view_items.html',context)


@never_cache
@login_required(login_url='admin-login')
def orderAccept(request,pk):
    if request.user.is_authenticated:
        Order.objects.filter(id=pk).update(approve_status=True)
        order = Order.objects.get(id=pk)
        items = order.orderitem_set.all()
    else:
        messages.error(request,'Something went wrong')
        return render(request,'dashboard/view_items.html')
    context = {'order':order,'items':items}
        
    return render(request,'dashboard/view_items.html',context)


@never_cache
@login_required(login_url='admin-login')
def orderShipped(request,pk):
    if request.user.is_authenticated:
        Order.objects.filter(id=pk).update(shipped_status=True)
        order = Order.objects.get(id=pk)
        items = order.orderitem_set.all()
    else:
        messages.error(request,'Something went wrong')
        return render(request,'dashboard/view_items.html')
    context = {'order':order,'items':items}
        
    return render(request,'dashboard/view_items.html',context)


@never_cache
@login_required(login_url='admin-login')
def orderDelivered(request,pk):
    if request.user.is_authenticated:
        Order.objects.filter(id=pk).update(delivery_status=True)
        order = Order.objects.get(id=pk)
        items = order.orderitem_set.all()
        payment = Payment.objects.filter(order=order).update(payment_status=True)
        print(payment)
    else:
        messages.error(request,'Something went wrong')
        return render(request,'dashboard/view_items.html')
    context = {'order':order,'items':items}
        
    return render(request,'dashboard/view_items.html',context)


