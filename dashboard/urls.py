from django.urls import path
from . import views

urlpatterns = [
    path('',views.adminLogin,name='admin-login'),
    path('logout',views.adminLogout,name='admin-logout'),
    path('admin-home',views.adminHome,name='admin-home'),
    path('user-view',views.viewUser,name='user-view'),
    path('block/<str:pk>',views.blockUser,name='user-block'),
    path('add-product',views.addProduct,name='add-product'),
    path('view-product',views.viewProduct,name='view-product'),
    path('edit-product/<str:pk>',views.editProduct,name='edit-product'),
    path('delete-product/<str:pk>',views.deleteProduct,name='delete-product'),
    path('delete-coupon/<str:pk>',views.deleteCoupon,name='delete-coupon'),
    path('add-category',views.addCategory,name='add-category'),
    path('edit-category/<str:pk>',views.editCategory,name='edit-category'),
    path('order-list',views.viewOrders,name='order-list'),
    path('return-view',views.returnOrderView,name='return-view'),
    path('order-items/<str:pk>',views.orderItemView,name='order-items'),
    path('order-accept/<str:pk>',views.orderAccept,name='order-accept'),
    path('order-shipped/<str:pk>',views.orderShipped,name='order-shipped'),
    path('order-delivered/<str:pk>',views.orderDelivered,name='order-delivered'),
    path('order-cancel-admin/<str:pk>/',views.orderCancelAdmin,name='order-cancel-admin'),
    path('sales-report/',views.salesReport,name='sales-report'),
    path('export-csv/',views.exportCsv,name='export-csv'),
    path('export-excel/',views.exportExcel,name='export-excel'),
    path('export-pdf/',views.exportPdf,name='export-pdf'),
    path('add-coupon/',views.addCoupon,name='add-coupon'),
    path('edit-coupon/<str:pk>',views.editCoupon,name='edit-coupon'),

]