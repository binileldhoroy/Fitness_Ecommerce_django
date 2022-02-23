from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.loginView,name='login'),
    path('logout/',views.logoutView,name='logout'),
    path('otp-login/',views.otpLogin,name='otp-login'),
    path('otp-verify/',views.otpVerify,name='otp-verify'),
    path('signup/',views.signupView,name='signup'),
    path('product/<str:pk>',views.productView,name='product'),
    path('cart/',views.cart,name='cart'),
    path('update-item/',views.updateCartItem,name='update-item'),
    path('check-out/',views.checkOut,name='check-out'),
    path('my-orders/',views.myOrders,name='my-orders'),
    path('order-cancel/<str:pk>',views.orderCancel,name='order-cancel'),
    path('payment-complete/',views.paymentComplete,name='payment-complete'),
    path('razorpay-payment/',views.payRazorpay,name='razorpay-payment'),
    path('check-out/razorpay-complete/',views.razorpayComplete,name='razorpay-complete'),
    path('my-profile/',views.myProfile,name='my-profile'),
    path('my-address/',views.myAddress,name='my-address'),
    path('delete-address/<str:pk>',views.deleteAddress,name='delete-address'),
    path('change-address/<str:pk>',views.changeAddress,name='change-address'),
    path('change-password/',views.MyPasswordChangeView.as_view(),name='change-password'),
    path('change-password/done',views.MyPasswordResetDoneView.as_view(),name='change-password-done'),
]