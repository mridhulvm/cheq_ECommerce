from django.db.models.expressions import Exists
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.views.decorators.cache import never_cache
from django.core.files.base import ContentFile
import base64


from accounts.models import Account
from category.models import Category
from product.models import Product
from orders.models import *


from .forms import CategoryForm, ProductForm

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
        context = {}
        return render(request, 'admin/index.html')

# -----------------------------------------------------------------CATEGORY


@never_cache
def addCategory(request):

    if request.session.get('admin_log'):
        form = CategoryForm()
        if request.method == 'POST':
            # print(request.POST)
            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                form = CategoryForm()

        context = {
            'form': form,
            'table_name': 'Add Category'
        }
        return render(request, 'admin/printForm.html', context)
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
        return render(request, 'admin/printForm.html', context)
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
            form = ProductForm(request.POST, request.FILES)
            print("POST cleared------------------")

            if form.is_valid():
                print("Form valid-------------------")
                cat = form.cleaned_data['category']
                product_name = form.cleaned_data['product_name']
                price = form.cleaned_data['price']
                stock = form.cleaned_data['stock']
                description = form.cleaned_data['description']
                slug = form.cleaned_data['slug']
                avail = form.cleaned_data['is_available']

                if request.POST.get('pro_img1'):
                    image1 = request.POST['pro_img1']
                    format, img1 = image1.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data1 = ContentFile(base64.b64decode(img1), name=product_name + '1.' + ext)
                else:
                    image1 = request.FILES['image1']

                  
                if request.POST.get('pro_img2'):
                    image2 = request.POST['pro_img2']
                    format, img2 = image2.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data2 = ContentFile(base64.b64decode(img2), name=product_name + '2.' + ext)
                else:
                    image2 = request.FILES['image2']

                if request.POST.get('pro_img3'):
                    image3 = request.POST['pro_img3']
                    format, img3 = image3.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data3 = ContentFile(base64.b64decode(img3), name=product_name + '3.' + ext)
                else:
                    image3 = request.FILES['image3']

                if request.POST.get('pro_img4'):
                    image4 = request.POST['pro_img4']
                    format, img4 = image4.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data4 = ContentFile(base64.b64decode(img4), name=product_name + '4.' + ext)
                else:
                    image4 = request.FILES['image4']
                
                product = Product(category=cat, product_name=product_name, price=price, stock=stock, description=description,
                                slug=slug, is_available=avail, image1=img_data1, image2=img_data2, image3=img_data3, image4=img_data4)
                product.save()
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
                cat = form.cleaned_data['category']
                product_name = form.cleaned_data['product_name']
                price = form.cleaned_data['price']
                stock = form.cleaned_data['stock']
                description = form.cleaned_data['description']
                slug = form.cleaned_data['slug']
                avail = form.cleaned_data['is_available']

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

                product_instance.category = cat
                product_instance.product_name = product_name
                product_instance.price = price
                product_instance.stock = stock
                product_instance.description = description
                product_instance.slug = slug
                product_instance.is_available = avail
                product_instance.save()
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
    print("--------------------id",id)
    if request.method == "GET":
        status=request.GET['status']
        print("--------------------------status",status)
        order_instance = OrderProduct.objects.get(id=id)
        order_instance.status = status
        order_instance.save()
    return redirect('viewOrder')
#  
