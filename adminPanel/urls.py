from django.urls import path
from . import views
 
urlpatterns = [
    path('',views.adminlogin,name="adminlogin"),     

    path('adminCheck',views.adminCheck,name="adminCheck"),
    path('adminSignout',views.adminSignout,name="adminSignout"),
    path('adminhome',views.adminhome,name="adminhome"),

    path('viewCategory',views.viewCategory,name="viewCategory"),
    path('addCategory',views.addCategory,name="addCategory"),
    path('editCategory/<int:id>',views.editCategory,name="editCategory"),
    path('deleteCategory/<int:id>',views.deleteCategory,name="deleteCategory"),


    path('viewProduct',views.viewProduct,name="viewProduct"),
    path('addProduct',views.addProduct,name="addProduct"),
    path('editProduct/<int:id>',views.editProduct,name="editProduct"),
    path('availProduct/<int:id>',views.availProduct,name="availProduct"),
    path('deleteProduct/<int:id>',views.deleteProduct,name="deleteProduct"),

    path('viewOffer',views.viewOffer,name="viewOffer"),
    path('addOffer',views.addOffer,name="addOffer"),
    path('editProductOffer/<int:id>',views.editProductOffer,name="editProductOffer"),
    path('editCategoryOffer/<int:id>',views.editCategoryOffer,name="editCategoryOffer"),
    path('deleteCategoryOffer/<int:id>',views.deleteCategoryOffer,name="deleteCategoryOffer"),
    path('deleteProductOffer/<int:id>',views.deleteProductOffer,name="deleteProductOffer"),

    path('viewCoupon',views.viewCoupon,name="viewCoupon"),
    path('addCoupon',views.addCoupon,name="addCoupon"),
    path('editCoupon/<int:id>',views.editCoupon,name="editCoupon"),
    path('deleteCoupon/<int:id>',views.deleteCoupon,name="deleteCoupon"),
    path('availCoupon/<int:id>',views.availCoupon,name="availCoupon"),

    path('viewReferral',views.viewReferral,name="viewReferral"),
    path('addReferral',views.addReferral,name="addReferral"),
    path('availReferral/<int:id>',views.availReferral,name="availReferral"),






    path('viewUser',views.viewUser,name="viewUser"),
    path('accessUser/<int:id>',views.accessUser,name="accessUser"),

    path('viewOrder',views.viewOrder,name="viewOrder"),
    path('statusOrder/<int:id>',views.statusOrder,name="statusOrder"),

    path('salesReport',views.salesReport,name="salesReport"),
    path('datewiseReport',views.datewiseReport,name="datewiseReport"),
    path('monthlyReport',views.monthlyReport,name="monthlyReport"),
    path('yearlyReport',views.yearlyReport,name="yearlyReport"),







]
