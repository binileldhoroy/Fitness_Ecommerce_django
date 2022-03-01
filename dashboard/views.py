from encodings import utf_8
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from fitness.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import CouponForm, ProductForm,CategoryForm
from .models import *
from django.db.models import Sum
from datetime import datetime
import csv
import xlwt
from django.template.loader import get_template

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
        #order Details
        approved = Order.objects.filter(approve_status = True).count()
        shipped = Order.objects.filter(shipped_status = True).count()
        delivered = Order.objects.filter(delivery_status = True).count()
        orders = [approved,shipped,delivered]
        
        #Payment details
        cod = Payment.objects.filter(payment_method='cod').aggregate(Sum('payment_amount'))
        razor = Payment.objects.filter(payment_method='razorpay').aggregate(Sum('payment_amount'))
        paypal = Payment.objects.filter(payment_method='paypal').aggregate(Sum('payment_amount'))
        
        cod_amt = cod['payment_amount__sum']
        razor_amt = razor['payment_amount__sum']
        paypal_amt = paypal['payment_amount__sum']
        paymethod = [cod_amt,razor_amt,paypal_amt]
        # strftime("%d/%m/%Y %H:%M:%S")

        products = Product.objects.all()

        prod = []
        st = []
        for product in products:
            prod.append(product.product_name[0:10])
            st.append(product.stock)

        context = {'count':orders,'paymethod':paymethod,'products':products,'prod':prod,'stock':st}
        return render(request,'dashboard/dash_home.html',context)
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
    if request.user.username == 'binil':
        user = User.objects.get(id=pk)
        if user.adminstatus == False:
            User.objects.filter(id=pk).update(adminstatus=True)
            return redirect('user-view')
        else:
            User.objects.filter(id=pk).update(adminstatus=False)
            return redirect('user-view')
    else:
        return redirect('login')
@never_cache
@login_required(login_url='admin-login')
def addProduct(request):
    if request.user.username == 'binil':
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
    else:
        return redirect('login')

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


@never_cache
@login_required(login_url='admin-login')
def salesReport(request):
    
    global orders
    orders = Order.objects.filter(payment__payment_status=True)

    if request.method == 'POST':
        s_date = request.POST.get('sdate')
        e_date = request.POST.get('edate')
        orders = orders.filter(date__range=[s_date,e_date]).filter(payment__payment_status=True)
        context = {'orders':orders}
        return render(request,'dashboard/sales_report.html',context)

    context = {'orders':orders}
    return render(request,'dashboard/sales_report.html',context)


@never_cache
@login_required(login_url='admin-login')
def exportCsv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=SalesReport'+str(datetime.now())+'.csv'

    writer = csv.writer(response)
    writer.writerow(['Order Id','Date','Payment Method','Items','Total Amount'])
    try:
        report_total = 0
        print(orders)
        for order in orders:
            writer.writerow([order.id,order.date,order.payment.payment_method,order.get_cart_items,order.payment.payment_amount])
            report_total = report_total + order.payment.payment_amount
        writer.writerow(['Total:-',report_total])
    except:
        messages.error(request,'Empty Order')
    return response


def exportExcel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=SalesReport'+str(datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding=utf_8)
    ws = wb.add_sheet('SalesReport')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Order Id','Date','Payment Method','Total Amount']

    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style = xlwt.XFStyle()

    rows = orders.values_list(
        'id','date','payment__payment_method','payment__payment_amount'
    )

    for row in rows:
        row_num = row_num + 1

        for col_num in range(len(columns)):
             ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response


def exportPdf(request):

    template_path = 'dashboard/pdf_downlad.html'
    context = {'order': orders}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="SalesReport'+str(datetime.now())+'.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    # pisa_status = pisa.CreatePDF(
    #    html, dest=response)
    # if error then show some funy view
    # if pisa_status.err:
    #    return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response



def addCoupon(request):
    form = CouponForm()
    coupons = Coupon.objects.all()
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add-coupon')
    context = {'form':form,'coupons':coupons}
    return render(request,'dashboard/add_coupon.html',context)