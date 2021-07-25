from django.db.models.expressions import Exists
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.views.decorators.cache import never_cache
from django.core.files.base import ContentFile
import base64

from django.db.models import Count,Sum,F

from django.http import HttpResponse

from accounts.models import Account
from category.models import Category,CategoryOffer
from product.models import Product,ProductOffer
from orders.models import Order,Payment,OrderProduct
from referral.models import ReferralControl,Referral,ReferralUsers


from .forms import *

db = {'name': 'mridhul', 'password': '12345678'}


# Create your views here.
@never_cache
def adminlogin(request):

    if request.session.get('admin_log'):
        return redirect('adminhome')
    else:
        return render(request, 'admin/login.html')


def adminCheck(request):

    admin = request.POST.get('adminname')
    adminpassword = request.POST.get('adminpassword')

    if admin == db['name'] and adminpassword == db['password']:
        request.session['admin_log'] = True
        return redirect('adminhome')

    elif admin != db['name']:
        messages.info(request, 'Invalid admin name')
        return redirect('adminlogin')

    elif adminpassword != db['password']:
        messages.info(request, 'Invalid admin name/password')
        return redirect('adminlogin')
    else:
        messages.info(request, 'Resubmit')
        return redirect('adminlogin')


def adminSignout(request):
    if request.session.get('admin_log'):
        del request.session['admin_log']
    # request.session.flush()
    return redirect('adminlogin')


@never_cache
def adminhome(request):
    if request.session.get('admin_log') != True:
        return redirect('adminlogin')
    else:
        completed_order= OrderProduct.objects.filter(status = "Delivered")
        sales = OrderProduct.objects.aggregate(sales=Sum( F('product_price')*F('quantity') ))['sales']
        products = Product.objects.all()

        paypal_orders =Payment.objects.filter(payment_method='PayPal').aggregate(paypal_orders=Sum('amount_paid'))['paypal_orders']
        cod_orders =Payment.objects.filter(payment_method='COD').aggregate(cod_orders=Sum('amount_paid'))['cod_orders']
        razorpay_orders =Payment.objects.filter(payment_method='Razorpay').aggregate(razorpay_orders=Sum('amount_paid'))['razorpay_orders']


        # stock=0
        # for product in products:
        #     stock +=product.price*product.stock
        stock = Product.objects.aggregate(stock=Sum(F('stock') * F('price') ))['stock']


        print("----------------------------------delivered---",completed_order)
        revenue=0
        for one_order in completed_order:
            revenue += one_order.product_price*one_order.quantity

        print("revenue---------------------------",revenue,sales)
        context = {
            "completed_order":completed_order,
            "revenue":revenue,
            "sales":sales,
            "stock":stock,
            "paypal_orders":paypal_orders,
            "cod_orders":cod_orders,
            'razorpay_orders':razorpay_orders,
        }
        return render(request, 'admin/index.html', context)
#------------------------------------------------------------------SALES REPORT  

def salesReport(request):
    orders=Order.objects.filter(is_ordered=True)
    context ={
    "orders":orders,
    }
    return render(request, 'admin/salesReport.html', context)

def datewiseReport(request):
    if request.GET.get('start') and request.GET.get('end'):
        start_date=request.GET.get('start')
        end_date=request.GET.get('end')
        orders=Order.objects.filter(is_ordered=True,updated_at__range=[start_date,end_date])

    else:   
        orders=Order.objects.filter(is_ordered=True)
    context ={
    "orders":orders,
    }
    return render(request, 'admin/salesReport.html', context)

def monthlyReport(request):
    if request.GET.get('month') and request.GET.get('year'):
        month=request.GET.get('month')
        year=request.GET.get('year')
        print(month,year)
        orders=Order.objects.filter(is_ordered=True)

    else:   
        orders=Order.objects.filter(is_ordered=True)    
    context ={
    "orders":orders,
    }
    return render(request, 'admin/salesReport.html', context)

def yearlyReport(request):
    if request.GET.get('year'):
        year=request.GET.get('year')
        print(year)
        orders=Order.objects.filter(is_ordered=True,updated_at__year=[year])

    else:   
        orders=Order.objects.filter(is_ordered=True)    
    context ={
    "orders":orders,
    }
    return render(request, 'admin/salesReport.html', context)



# -----------------------------------------------------------------CATEGORY


@never_cache
def addCategory(request):

    if request.session.get('admin_log'):
        form = CategoryForm()
        if request.method == 'POST':
            # print(request.POST)
            form = CategoryForm(request.POST, request.FILES)

            if form.is_valid():
                category_instance= Category()  

                category_name = form.cleaned_data['category_name']
                slug = form.cleaned_data['slug']
                description = form.cleaned_data['description']
                avail = form.cleaned_data['is_available']  

                if request.POST.get('offer_percentage'):
                    offer_percentage = form.cleaned_data['offer_percentage']
                    category_instance.offer_percentage = offer_percentage

               

                image1 = request.POST['pro_img1']
                format, img1 = image1.split(';base64,')
                ext = format.split('/')[-1]
                img_data1 = ContentFile(base64.b64decode(img1), name=category_name + '1.' + ext)

                category_instance.category_name = category_name
                category_instance.slug = slug
                category_instance.is_available = avail
                category_instance.description = description
                category_instance.cat_image = img_data1
                category_instance.save()
                messages.success(request, 'Category Added successfully')
                form = CategoryForm()

        context = {
            'form': form,
            'table_name': 'Add Category'
        }
        return render(request, 'admin/addCategory.html', context)
    else:
        return redirect('adminlogin')


@never_cache
def viewCategory(request):
    if request.session.get('admin_log'):

        obj = Category.objects.all()
        context = {
            'Categories': obj
        }
        return render(request, 'admin/viewCategory.html', context)

    else:
        return redirect('adminlogin')


@never_cache
def editCategory(request, id):
    if request.session.get('admin_log'):

        if request.method == 'POST':
            product_instance = Category.objects.get(id=id)
            form = CategoryForm(request.POST, request.FILES,
                                instance=product_instance)
            if form.is_valid():
                form.save()
                return redirect('viewCategory')

        else:
            category_instance = Category.objects.get(id=id)
            form = CategoryForm(instance=category_instance)

        context = {
            'form': form,
            'table_name': 'Edit Category'

        }
        return render(request, 'admin/editCategory.html', context)
    else:
        return redirect('adminlogin')

def deleteCategory(request,id):
    if Category.objects.filter(id=id).exists():
        Category_instance = Category.objects.get(id=id)
        Category_instance.delete()
        return redirect('viewCategory')
    else:
        return redirect('viewCategory')

# -----------------------------------------------------------------PRODUCT
@never_cache
def viewProduct(request):
    if request.session.get('admin_log'):

        obj = Product.objects.all()
        obj2 = Category.objects.all()
        context = {
            'Products': obj,
            'categories': obj2
        }
        print(obj2)
        return render(request, 'admin/viewProduct.html', context)
    else:
        return redirect('adminlogin')


@never_cache
def addProduct(request):
    if request.session.get('admin_log'):

        form = ProductForm()
        print("session cleared-------------------")
        if request.method == 'POST':
            print("POST cleared------------------")

            form = ProductForm(request.POST, request.FILES)

            if form.is_valid():
                print("Form valid-------------------")
                product_instance= Product()         
                cat = form.cleaned_data['category']
                product_name = form.cleaned_data['product_name']
                price = form.cleaned_data['price']
                stock = form.cleaned_data['stock']
                description = form.cleaned_data['description']
                slug = form.cleaned_data['slug']
                avail = form.cleaned_data['is_available']

                if request.POST.get('offer_price'):
                    offer_price = form.cleaned_data['offer_price']
                    product_instance.offer_price = offer_price

                if request.POST.get('offer_percentage'):
                    offer_percentage = form.cleaned_data['offer_percentage']
                    product_instance.offer_percentage = offer_percentage



                if request.POST.get('pro_img1'):
                    image1 = request.POST['pro_img1']
                    format, img1 = image1.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data1 = ContentFile(base64.b64decode(img1), name=product_name + '1.' + ext)
                # else:
                #     image1 = request.FILES['image1']

                  
                if request.POST.get('pro_img2'):
                    image2 = request.POST['pro_img2']
                    format, img2 = image2.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data2 = ContentFile(base64.b64decode(img2), name=product_name + '2.' + ext)
                # else:
                #     image2 = request.FILES['image2']

                if request.POST.get('pro_img3'):
                    image3 = request.POST['pro_img3']
                    format, img3 = image3.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data3 = ContentFile(base64.b64decode(img3), name=product_name + '3.' + ext)
                # else:
                #     image3 = request.FILES['image3']

                if request.POST.get('pro_img4'):
                    image4 = request.POST['pro_img4']
                    format, img4 = image4.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data4 = ContentFile(base64.b64decode(img4), name=product_name + '4.' + ext)
                # else:
                #     image4 = request.FILES['image4']
                
                # product = Product(category=cat, product_name=product_name, price=price, stock=stock, description=description,
                #                 slug=slug, is_available=avail, image1=img_data1, image2=img_data2, image3=img_data3, image4=img_data4)

                product_instance.image1 = img_data1
                product_instance.image2 = img_data2
                product_instance.image3 = img_data3     
                product_instance.image4 = img_data4                    

                product_instance.category = cat
                product_instance.product_name = product_name
                product_instance.price = price
                product_instance.stock = stock
                product_instance.description = description
                product_instance.slug = slug
                product_instance.is_available = avail
          
                product_instance.save()

                messages.success(request, 'Product Added successfully')
                form = ProductForm()
            else:
                print("form not valid")

        context = {
            'form': form,
            'table_name': 'Add Product'
        }
        print("page rendering-------------------------")
        return render(request, 'admin/addProduct.html', context)
    else:
        return redirect('adminlogin')


@never_cache
def editProduct(request, id):
    if request.session.get('admin_log'):

        if request.method == 'POST':
            product_instance = Product.objects.get(id=id)
            form = ProductForm(request.POST, request.FILES,instance=product_instance)
            if form.is_valid():

                if request.POST.get('category'):
                    cat = form.cleaned_data['category']
                    product_instance.category = cat


                if request.POST.get('product_name'):
                    product_name = form.cleaned_data['product_name']
                    product_instance.product_name = product_name

                if request.POST.get('price'):
                    price = form.cleaned_data['price']
                    product_instance.price = price

                if request.POST.get('stock'):
                    stock = form.cleaned_data['stock']
                    product_instance.stock = stock

                if request.POST.get('description'):
                    description = form.cleaned_data['description']
                    product_instance.description = description

                if request.POST.get('slug'):
                    slug = form.cleaned_data['slug']
                    product_instance.slug = slug

                if request.POST.get('is_available'):
                    avail = form.cleaned_data['is_available']
                    product_instance.is_available = avail
                
                    
                
                
                

                # if request.POST.get('offer_percentage'):
                #     offer_percentage = form.cleaned_data['offer_percentage']
                #     product_instance.offer_percentage = offer_percentage



                if request.POST.get('pro_img1'):
                    image1 = request.POST['pro_img1']
                    format, img1 = image1.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data1 = ContentFile(base64.b64decode(img1), name=product_name + '1.' + ext)
                    product_instance.image1 = img_data1
                  
                if request.POST.get('pro_img2'):
                    image2 = request.POST['pro_img2']
                    format, img2 = image2.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data2 = ContentFile(base64.b64decode(img2), name=product_name + '2.' + ext)
                    product_instance.image2 = img_data2

                if request.POST.get('pro_img3'):
                    image3 = request.POST['pro_img3']
                    format, img3 = image3.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data3 = ContentFile(base64.b64decode(img3), name=product_name + '3.' + ext)
                    product_instance.image3 = img_data3     

                if request.POST.get('pro_img4'):
                    image4 = request.POST['pro_img4']
                    format, img4 = image4.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data4 = ContentFile(base64.b64decode(img4), name=product_name + '4.' + ext)
                    product_instance.image4 = img_data4                    

                if request.POST.get('offer_price'):

                    offer_price = form.cleaned_data['offer_price']
                    product_instance.offer_price = offer_price


           

                if product_instance.offer_price == None:
                    product_instance.offer_percentage = None
                else:
                    current_offer_percentage= int(  (product_instance.price - product_instance.offer_price ) / product_instance.price *100  ) #find % according to price if % not given
                    product_instance.offer_percentage = current_offer_percentage
            


                product_instance.save()

                # if  ProductOffer.objects.filter(product=product_instance.id).exists() and request.POST.get('offer_price'): #to change from productOffer table if offer price changes
                #     product_offer_instance=ProductOffer.objects.get(product=product_instance.id)
                    # if product_instance.offer_percentage != product_offer_instance.offer:
                    #     product_offer_instance.offer = product_instance.offer_percentage
                    #     product_offer_instance.save()

                    # calculated_offer_price= int(product_instance.price *(100-product_offer_instance.offer)*100)#if offer price is changed productOffer table is deleted as it is not neccessary

                    # if product_instance.offer_price !=  calculated_offer_price :
                    
                    #     product_offer_instance.delete()


                return redirect('viewProduct')

        else:
            product_instance = Product.objects.get(id=id)
            form = ProductForm(instance=product_instance)

        context = {
            'form': form,
            'table_name': 'Edit Product'
        }
        return render(request, 'admin/editProduct.html', context)
    else:
        return redirect('adminlogin')


def availProduct(request, id):
    product_instance = Product.objects.get(id=id)
    if product_instance.is_available == True:
        product_instance.is_available = False
    else:
        product_instance.is_available = True
    product_instance.save()
    return redirect('viewProduct')

def deleteProduct(request,id):
    if Product.objects.filter(id=id).exists():
        product_instance = Product.objects.get(id=id)
        product_instance.delete()
        return redirect('viewProduct')
    else:
        return redirect('viewProduct')



# -----------------------------------------------------------------USER


@never_cache
def viewUser(request):
    if request.session.get('admin_log'):

        obj = Account.objects.all()
        context = {
            'Users': obj
        }
        print(obj)
        return render(request, 'admin/viewUser.html', context)
    else:
        return redirect('adminlogin')


def accessUser(request, id):
    account_instance = Account.objects.get(id=id)
    if account_instance.is_active:
        account_instance.is_active = False
    else:
        account_instance.is_active = True
    account_instance.save()
    return redirect('viewUser')
#----------------------------------------------------------------Orders

@never_cache
def viewOrder(request):
    if request.session.get('admin_log'):

        obj = OrderProduct.objects.all()
        context = {
            'orders': obj,

        }
        return render(request, 'admin/viewOrder.html', context)
    else:
        return redirect('adminlogin')

def statusOrder(request,id):
    if request.method == "GET":

        status=request.GET.get('status')

        print(status)
        order_instance = OrderProduct.objects.get(id=id)
        if status :
            order_instance.status = status
            order_instance.save()
        
    return redirect('viewOrder')

# ------------------------------------------------------------OFFERS--------------
@never_cache
def viewOffer(request):
    if request.session.get('admin_log'):

        catergories = CategoryOffer.objects.all()
        products = ProductOffer.objects.all()

        context = {
            'catergories':catergories ,
            'products':products,

        }
        return render(request, 'admin/viewOffer.html', context)
    else:
        return redirect('adminlogin')

def addOffer(request):
    if request.session.get('admin_log'):
        Categoryform = CategoryOfferForm()
        ProductForm = ProductOfferForm()
        
        if request.method == 'POST':

            Categoryform = CategoryOfferForm(request.POST)
            ProductForm = ProductOfferForm(request.POST)
            
            if ProductForm.is_valid(): #if product form updated

                product_name = ProductForm.cleaned_data['product']
                offer = ProductForm.cleaned_data['offer']
                start = ProductForm.cleaned_data['offer_start']
                end = ProductForm.cleaned_data['offer_end']
    
                product = ProductOffer(product = product_name ,offer = offer, offer_start = start,offer_end = end)
                product.save()

                # if product.check_expired:
                #     pass
                # else:
                product_instance=Product.objects.get(id=product.product.id)
                product_instance.offer_percentage=offer
                product_instance.offer_price = int(product_instance.price*(100 - offer)/100)
                product_instance.save()

                messages.success(request, 'Product Offer Added successfully')

                ProductForm = ProductOfferForm()
                Categoryform = CategoryOfferForm()

            else:
                print("ProductForm not valid")

            if Categoryform.is_valid(): #if category form updated

                cat = Categoryform.cleaned_data['category']
                offer = Categoryform.cleaned_data['offer']
                start = Categoryform.cleaned_data['offer_start']
                end = Categoryform.cleaned_data['offer_end']
                print(cat,offer,start,end)

                category_offer_instance = CategoryOffer(category=cat,offer = offer,offer_start = start,offer_end = end)
                category_offer_instance.save()
                
                #save in category
                category_instance = Category.objects.get(id = category_offer_instance.category.id )
                category_instance.offer_percentage=offer
                category_instance.save()

                #save in product
                product_instances=Product.objects.filter(category=category_offer_instance.category)#change offer of all category Products
                # if category.check_expired:
                #     pass 
                # else:
                for product_instance in product_instances:
                    product_instance.offer_percentage=offer
                    product_instance.offer_price = int(product_instance.price*(100-offer)/100)
                    product_instance.save() 

                messages.success(request, 'Category Offer Added successfully')

                Categoryform = CategoryOfferForm()
                ProductForm = ProductOfferForm()


            else:
                print("Categoryform not valid")

        context = {
            'Categoryform': Categoryform,
            'ProductForm':ProductForm,
            'table_name1':"Add Category Offer",
            'table_name2':"Add Product Offer"
        }
        print("page rendering-------------------------")
        return render(request, 'admin/addOffer.html', context)
    else:
        return redirect('adminlogin')

        
def editProductOffer(request,id):

    if request.session.get('admin_log'):  

        product_offer_instance = ProductOffer.objects.get(id = id)
        if request.method == 'POST':

            ProductForm = ProductOfferForm(request.POST,instance = product_offer_instance)
            
            if ProductForm.is_valid(): #if product form updated

                product_name = ProductForm.cleaned_data['product']
                offer = ProductForm.cleaned_data['offer']
                start = ProductForm.cleaned_data['offer_start']
                end = ProductForm.cleaned_data['offer_end']
    
                product_offer_instance.product = product_name 
                product_offer_instance.offer = offer
                product_offer_instance.offer_start = start
                product_offer_instance.offer_end = end
                product_offer_instance.save()

                product_instance=Product.objects.get(id=product_offer_instance.product.id)
                product_instance.offer_percentage=offer
                product_instance.offer_price = int(product_instance.price*(100-offer)/100)
                product_instance.save()

                return redirect ('viewOffer')
            else:
                print("ProductForm not valid")
        else:
            ProductForm = ProductOfferForm(instance = product_offer_instance)        


        context = {
            'ProductForm':ProductForm,
        }
        print("page rendering-------------------------")
        return render(request, 'admin/editProductOffer.html', context)
    else:
        return redirect('adminlogin')

def editCategoryOffer(request,id):

    if request.session.get('admin_log'):  
        category_offer_instance = CategoryOffer.objects.get(id=id)

        if request.method == 'POST':

            Categoryform = CategoryOfferForm(request.POST,instance = category_offer_instance)

            if Categoryform.is_valid(): #if category form updated

                cat = Categoryform.cleaned_data['category']
                offer = Categoryform.cleaned_data['offer']
                start = Categoryform.cleaned_data['offer_start']
                end = Categoryform.cleaned_data['offer_end']
                print(cat,offer,start,end)

                category_offer_instance.category=cat
                category_offer_instance.offer = offer
                category_offer_instance.offer_start = start
                category_offer_instance.offer_end = end
                category_offer_instance.save()

                category_instance = Category.objects.get(id = category_offer_instance.category.id)
                category_instance.offer_percentage = offer
                category_instance.save()

                product_instances=Product.objects.all().filter(category=category_instance)
                # if category_offer_instance.check_expired:
                #     for product_instance in product_instances:
                #         product_instance.offer_percentage=None
                #         product_instance.offer_price = None
                #         product_instance.save()  

                # else:
                for product_instance in product_instances:
                    product_instance.offer_percentage=offer
                    product_instance.offer_price = int(product_instance.price*(100-offer)/100)
                    product_instance.save()                
                return redirect ('viewOffer')

            else:
                print("Categoryform not valid")

        else:
            Categoryform = CategoryOfferForm(instance = category_offer_instance)

        context = {
            'Categoryform':Categoryform,
        }
        print("page rendering-------------------------")
        return render(request, 'admin/editCategoryOffer.html', context)
    else:
        return redirect('adminlogin')

def deleteCategoryOffer(request,id):
    if CategoryOffer.objects.filter(id=id).exists():
        Category_offer_instance = CategoryOffer.objects.get(id=id)

        category = Category.objects.get(id = Category_offer_instance.category.id)
        category.offer = None

        product_instances=Product.objects.filter(category=Category_offer_instance.id)
        for product_instance in product_instances:
            if product_instance.offer_percentage == None:
                 pass
            else:
                product_instance.offer_percentage = None
                product_instance.offer_price = None
                product_instance.save()  
        Category_offer_instance.delete()
        return redirect('viewOffer')
    else:
        return redirect('viewOffer')

def deleteProductOffer(request,id):
    if ProductOffer.objects.filter(id=id).exists():

        Product_offer_instance = ProductOffer.objects.get(id=id)

        product_instance=Product.objects.get(id= Product_offer_instance.product.id)
       
        product_instance.offer_percentage = None
        product_instance.offer_price = None
        product_instance.save()  

        Product_offer_instance.delete()
        return redirect('viewOffer')
    else:
        return redirect('viewOffer')
#====================================================================COUPON======
@never_cache
def viewCoupon(request):
    if request.session.get('admin_log'):

        coupons = Coupon.objects.all()

        context = {
            'coupons':coupons ,

        }
        return render(request, 'admin/viewCoupon.html', context)
    else:
        return redirect('adminlogin')
        
def addCoupon(request):
    if request.session.get('admin_log'):

        couponform = CouponForm()
        
        if request.method == 'POST':

            couponform = CouponForm(request.POST)
            
            if couponform.is_valid(): #if product form updated

                coupon_title = couponform.cleaned_data['coupon_title']
                coupon_limit = couponform.cleaned_data['coupon_limit']


                coupon_offer = couponform.cleaned_data['coupon_offer']
                coupon_start = couponform.cleaned_data['coupon_start']
                coupon_end = couponform.cleaned_data['coupon_end']
    
                coupon_instance = Coupon(coupon_title = coupon_title ,coupon_limit = coupon_limit,coupon_offer = coupon_offer, coupon_start = coupon_start,coupon_end = coupon_end)
                coupon_instance.save()

        

                messages.success(request, 'Coupon Added successfully')

                couponform = CouponForm()

            else:
                print("CouponForm not valid")


        context = {
            'couponform': couponform,
            'table_name':"Add Coupon"
         
        }
        print("page rendering-------------------------")
        return render(request, 'admin/addCoupon.html', context)
    else:
        return redirect('adminlogin')


def editCoupon(request,id):

    if request.session.get('admin_log'):  

        coupon_instance = Coupon.objects.get(id = id)

        if request.method == 'POST':

            couponform = CouponForm(request.POST,instance = coupon_instance)
            
            if couponform.is_valid(): #if product form updated

                coupon_title = couponform.cleaned_data['coupon_title']
                coupon_limit = couponform.cleaned_data['coupon_limit']


                coupon_offer = couponform.cleaned_data['coupon_offer']
                coupon_start = couponform.cleaned_data['coupon_start']
                coupon_end = couponform.cleaned_data['coupon_end']


                coupon_instance.coupon_title = coupon_title 
                coupon_instance.coupon_limit = coupon_limit
                coupon_instance.coupon_offer = coupon_offer 
                coupon_instance.coupon_start = coupon_start
                coupon_instance.coupon_end = coupon_end
                coupon_instance.save()

        


                return redirect ('viewCoupon')
            else:
                print("couponform not valid")
        else:
            couponform = CouponForm(instance = coupon_instance)        


        context = {
            'couponform':couponform,
            'table_name':"Edit Coupon"
        }
        print("page rendering-------------------------")
        return render(request, 'admin/addCoupon.html', context)
    else:
        return redirect('adminlogin')


def availCoupon(request, id):
    
    coupon_instance = Coupon.objects.get(id=id)
    if coupon_instance.is_available == True:
        coupon_instance.is_available = False
    else:
        coupon_instance.is_available = True
    coupon_instance.save()
    return redirect('viewCoupon')

def deleteCoupon(request,id):
    if Coupon.objects.filter(id=id).exists():
        coupon_instance = Coupon.objects.get(id=id)
        coupon_instance.delete()
        return redirect('viewCoupon')
    else:
        return redirect('viewCoupon')

#==============================================REFERRAL================================

@never_cache
def viewReferral(request):
    if request.session.get('admin_log'):

        referral_controls = ReferralControl.objects.all()
        referrals = Referral.objects.all()
        referred_users = ReferralUsers.objects.all()

        context = {
            'referral_controls':referral_controls ,
            'referrals':referrals,
            'referred_users':referred_users,

        }
        return render(request, 'admin/viewReferral.html', context)
    else:
        return redirect('adminlogin')

def availReferral(request, id):
    referral_control_instance = ReferralControl.objects.get(id=id)
    if referral_control_instance.is_available == True:
        referral_control_instance.is_available = False
    else:
        referral_control_instance.is_available = True
    referral_control_instance.save()
    return redirect('viewReferral')

@never_cache 
def addReferral(request):
    if request.session.get('admin_log'):
        count = ReferralControl.objects.all()
        if not count:
            control_instance = ReferralControl()
            referral_user_limit = None
            referral_percentage = None
            referral_percentage_limit = None
            referral_amount = None
         
            referral_enddate = None


        else:
            control_instance = ReferralControl.objects.first()
            referral_user_limit = control_instance.referral_user_limit
            referral_percentage = control_instance.referral_percentage
            referral_percentage_limit = control_instance.referral_percentage_limit
            referral_amount = control_instance.referral_amount
      
            referral_enddate = control_instance.referral_end_date
            is_available = control_instance.is_available

            print(control_instance.referral_user_limit)

        if request.method == 'POST':  
              
                user_limit = request.POST['referral_user_limit']
                control_instance.referral_user_limit = int(user_limit)

                referral_enddate  = request.POST['referral_end_date']
                control_instance.referral_end_date = referral_enddate

                # if request.POST.get('referral_percentage') :
                #     print("percentage================")
                #     percentage = request.POST['referral_percentage']
                #     percentage_limit = request.POST['referral_percentage_limit']
                #     print(percentage,percentage_limit,"===================")
                #     if percentage_limit == None or percentage_limit == None:
                #         pass
                #     else:
                #         print("else========================")
                #         control_instance.referral_percentage = int(percentage)
                #         control_instance.referral_percentage_limit = float(percentage_limit)

                #         control_instance.referral_amount = None

                if request.POST['referral_amount']:
                    print("amount================")
                    amount = request.POST['referral_amount']
                    control_instance.referral_amount = int(amount)

                    control_instance.referral_percentage = None
                    control_instance.referral_percentage_limit = None

                if request.POST.get('is_available'):
                    is_available = True
                else:              
                    is_available = False

                control_instance.is_available = is_available
    
                control_instance.save()
                return redirect('viewReferral')
        context={
            'referral_user_limit':referral_user_limit,
            'referral_enddate':referral_enddate,
            'is_available':is_available,
            'referral_percentage':referral_percentage,
            'referral_percentage_limit':referral_percentage_limit,
            'referral_amount':referral_amount,

        }
        return render(request, 'admin/addReferral.html',context)
    else:
        return redirect('adminlogin')
