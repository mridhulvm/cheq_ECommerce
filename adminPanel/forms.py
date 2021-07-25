from django.forms import ModelForm
from django import forms
from category.models import *
from product.models import *

class CategoryForm(ModelForm):
    cat_image = forms.ImageField(widget=forms.FileInput,)

    class Meta:
        model = Category
        fields = ('category_name','slug','cat_image','description','is_available')

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['category_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['slug'].widget.attrs.update({'class': 'form-control'})
        self.fields['cat_image'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_available'].widget.attrs.update({'class': 'form-check-input','type':'checkbox'})
              

class ProductForm(ModelForm):
    image1 = forms.ImageField(widget=forms.FileInput,)
    image2 = forms.ImageField(widget=forms.FileInput,)
    image3 = forms.ImageField(widget=forms.FileInput,)
    image4 = forms.ImageField(widget=forms.FileInput,)

    class Meta:
        model = Product
        fields = ('product_name','slug','description','price','image1','image2','image3','image4','stock','is_available','category')
#         widgets = {
#     'product_name': forms.TextInput(attrs={'class': 'form-group'}),
# }
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['slug'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['image1'].widget.attrs.update({'class': 'form-control'})
        self.fields['image2'].widget.attrs.update({'class': 'form-control'})
        self.fields['image3'].widget.attrs.update({'class': 'form-control'})
        self.fields['image4'].widget.attrs.update({'class': 'form-control'})
        self.fields['stock'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})

        self.fields['is_available'].widget.attrs.update({'class': 'form-check-input','type':'checkbox'})




class CategoryOfferForm(ModelForm):
    class Meta:
        model = CategoryOffer
        fields = '__all__'
        widgets = {
        'offer_start': forms.DateInput(format=('%Y-%m-%d'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
        'offer_end': forms.DateInput(format=('%Y-%m-%d'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(CategoryOfferForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['offer'].widget.attrs.update({'class': 'form-control'})
   
    
class ProductOfferForm(ModelForm):
    class Meta:
        model = ProductOffer
        fields = '__all__'
        widgets = {
            'offer_start': forms.DateInput(format=('%Y-%m-%d'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
            'offer_end': forms.DateInput(format=('%Y-%m-%d'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),

        } 

    def __init__(self, *args, **kwargs):
        super(ProductOfferForm, self).__init__(*args, **kwargs)
        self.fields['product'].widget.attrs.update({'class': 'form-control'})
        self.fields['offer'].widget.attrs.update({'class': 'form-control'})
      

class CouponForm(ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'
        widgets = {
        'coupon_start': forms.DateInput(format=('%Y-%m-%d'), attrs={'placeholder':'Select a date', 'type':'date'}),
        'coupon_end': forms.DateInput(format=('%Y-%m-%d'), attrs={ 'placeholder':'Select a date', 'type':'date'}),

        }

    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)
        self.fields['coupon_title'].widget.attrs.update({'class': 'form-control'})
        self.fields['coupon_limit'].widget.attrs.update({'class': 'form-control'})
        self.fields['coupon_offer'].widget.attrs.update({'class': 'form-control'})
        self.fields['coupon_start'].widget.attrs.update({'class': 'form-control'})
        self.fields['coupon_end'].widget.attrs.update({'class': 'form-control'})
        self.fields['coupon_start'].widget.attrs.update({'class': 'form-control'})

              

                        