
from django.conf import settings
from . import web as views
from . import ProductView
from django.urls import path


urlpatterns = [
    path('', views.home_view),
    path('customers/', views.customers_view),
    path('customers/delete/', views.customers_delete_view),
    path('banners/', views.banners_view),
    path('products/', ProductView.products_view),
    path('products/add/', ProductView.add_product_view),
    path('products/delete/', ProductView.products_delete_view),
    #login views
    path('login/',views.login_view)
]




