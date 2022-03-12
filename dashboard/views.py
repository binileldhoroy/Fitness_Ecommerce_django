from encodings import utf_8
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from fitness.models import *
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
from django.db.models import Q

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
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    if request.user.username == 'binil':
        products = Product.objects.filter(
        Q(product_name__icontains=q)|
        Q(description__icontains=q)|
        Q(category__name__icontains=q))
    else:
        return redirect('login')
    return render(request,'dashboard/view_product.html',{'products':products})


@never_cache
@login_required(login_url='admin-login')
def editProduct(request,pk):
    if request.user.username == 'binil':
        product = Product.objects.get(id=pk)
        form = ProductForm(instance=product)
        if request.method == 'POST':
            form = ProductForm(request.POST,instance=product)
            if form.is_valid():
                form.save()
                messages.success(request,'Update Successfully')
                return redirect('view-product')
    else:
        return redirect('login')
    return render(request,'dashboard/edit_product.html',{'form':form})


@never_cache
@login_required(login_url='admin-login')
def deleteProduct(request,pk):
    if request.user.username == 'binil':
        product = Product.objects.get(id=pk)
        if request.method == 'POST':
            product.delete()
            return redirect('view-product')
    else:
        return redirect('login')
    return render(request,'dashboard/delete_product.html')

@never_cache
@login_required(login_url='admin-login')
def addCategory(request):
    if request.user.username == 'binil':
        form = CategoryForm()
        category = Category.objects.all()
        if request.method == 'POST':
            category = request.POST.get('name')
            Category.objects.get_or_create(name=category)
            messages.success(request,'Cateory is Added')
            return redirect('add-category')
        
        return render(request,'dashboard/dash_addproduct.html',{'form':form,'category':category})
    else:
        return redirect('login')


@never_cache
@login_required(login_url='admin-login')
def editCategory(request,pk):
    if request.user.username == 'binil':
        cat = Category.objects.get(id=pk)
        form = CategoryForm(instance=cat)
        if request.method == 'POST':
            form = CategoryForm(request.POST,instance=cat)
            if form.is_valid():
                form.save()
                messages.success(request,'Update Successfully')
                return redirect('add-category')
        
        return render(request,'dashboard/edit_category.html',{'form':form})
    else:
        return redirect('login')


@never_cache
@login_required(login_url='admin-login')
def viewOrders(request):
    if request.user.username == 'binil':
        if request.user.is_authenticated:
            orders = Order.objects.all().filter(order_status=True)
        else:
            messages.error(request,'Empty Orders')
            return render(request,'dashboard/view_orders.html')
        context = {'orders':orders}
    else:
        return redirect('login')  

    return render(request,'dashboard/view_orders.html',context)


@never_cache
@login_required(login_url='admin-login')
def orderItemView(request,pk):
    if request.user.username == 'binil':
        if request.user.is_authenticated:
            order = Order.objects.get(id=pk)
            items = order.orderitem_set.all()
        else:
            messages.error(request,'Something went wrong')
            return render(request,'dashboard/view_items.html')
        context = {'order':order,'items':items} 
    else:
        return redirect('login')   

    return render(request,'dashboard/view_items.html',context)


@never_cache
@login_required(login_url='admin-login')
def orderAccept(request,pk):
    if request.user.username == 'binil':
        if request.user.is_authenticated:
            Order.objects.filter(id=pk).update(approve_status=True)
            order = Order.objects.get(id=pk)
            items = order.orderitem_set.all()
        else:
            messages.error(request,'Something went wrong')
            return render(request,'dashboard/view_items.html')
        context = {'order':order,'items':items}
    else:
        return redirect('login')  
    return render(request,'dashboard/view_items.html',context)


@never_cache
@login_required(login_url='admin-login')
def orderShipped(request,pk):
    if request.user.username == 'binil':
        if request.user.is_authenticated:
            Order.objects.filter(id=pk).update(shipped_status=True)
            order = Order.objects.get(id=pk)
            items = order.orderitem_set.all()
        else:
            messages.error(request,'Something went wrong')
            return render(request,'dashboard/view_items.html')
        context = {'order':order,'items':items}
    else:
        return redirect('login')        
    return render(request,'dashboard/view_items.html',context)


@never_cache
@login_required(login_url='admin-login')
def orderDelivered(request,pk):
    if request.user.username == 'binil':
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
    else:
        return redirect('login')    
    return render(request,'dashboard/view_items.html',context)


@never_cache
@login_required(login_url='login')
def orderCancelAdmin(request,pk):
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
        return redirect('order-list')
    else:
        messages.error(request,'Something went wrong')
        return render(request,'fitness/myorders.html')


@never_cache
@login_required(login_url='admin-login')
def salesReport(request):
    if request.user.username == 'binil':
        global orders
        num = 2000
        yr = []
        for i in range(50):
            yr.append(num+i)
        orders = Order.objects.filter(payment__payment_status=True)
        if request.method == 'POST':
            datestr = request.POST.get('dates')
            #start date
            mo = datestr[:2]
            da = datestr[3:5]
            ye = datestr[6:10]
            #enddate
            mo1 = datestr[13:15]
            da1 = datestr[16:18]
            ye1 = datestr[19:]
            s_date = ye+'-'+mo+'-'+da
            e_date = ye1+'-'+mo1+'-'+da1
            print(s_date)
            print('.......',e_date)
            month = request.POST.get('month')
            year = request.POST.get('year')
            print(year)
            if month != '':
                m = int(month[5:])
                orders = orders.filter(date__month=m).filter(payment__payment_status=True)
                print(orders)
            elif year != '':
                y = int(year)
                orders = orders.filter(date__year=y).filter(payment__payment_status=True)
            elif s_date == '' and e_date == '' and month == '' and year == '':
                messages.error(request,'Select a date')
                return redirect('sales-report')
            else:
                orders = orders.filter(date__range=[s_date,e_date]).filter(payment__payment_status=True)
            context = {'orders':orders,'yr':yr}
            return render(request,'dashboard/sales_report.html',context)

        context = {'orders':orders,'yr':yr}
    else:
        return redirect('login')
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
    if request.user.username == 'binil':
        form = CouponForm()
        coupons = Coupon.objects.all()
        if request.method == 'POST':
            form = CouponForm(request.POST)
            coupon_date = request.POST.get('coupon_date')
            print(coupon_date)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.valid_to = coupon_date
                instance.save()
                return redirect('add-coupon')
        context = {'form':form,'coupons':coupons}
    else:
        return redirect('login')
    return render(request,'dashboard/add_coupon.html',context)