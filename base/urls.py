from . import views
from django.urls import path 
from django.contrib.auth import views as auth_views




urlpatterns = [  
    path('', views.home, name='home'),
    path('register/' , views.register, name ='register'),
    path('login/',auth_views.LoginView.as_view(template_name ='login.html'), name = 'login'),
    path('logout/',auth_views.LogoutView.as_view(template_name ='logout.html'), name = 'logout'),
    path('accounts/profile/' , views.profile  , name='profile'),
    path('paypal-return/', views.PaypalReturnView.as_view(), name='paypal-return'),
    path('paypal-cancel/', views.PaypalCancelView.as_view(), name='paypal-cancel'),
    path('process-payment/' , views.PaypalFormView.as_view() , name='paypal'),
    path('accounts/profile/' , views.profile  , name='profile'),
    path('subscription-selection/' , views.subscription , name='subscription'),
    path('competitor-web-analysis/' , views.crawl_website_properly , name='crawl'),


]
