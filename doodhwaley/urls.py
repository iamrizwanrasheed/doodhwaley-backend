"""doodhwaley URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from rest_framework import routers
from milkapp.views.api import api as api_views
from knox.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework.urlpatterns import format_suffix_patterns

from milkapp.views.web import urls as web_urls
from milkapp.views.web.web import home_page

router = routers.DefaultRouter()
router.register(r'deliveryboy', api_views.DeliveryBoyViewSet)
router.register(r'store', api_views.StoreViewSet)
router.register(r'customer', api_views.CustomerViewSet)
router.register(r'order', api_views.OrderViewSet)
router.register(r'order-product', api_views.OrderProductViewSet)
router.register(r'product', api_views.ProductViewSet)
router.register(r'product-category', api_views.ProductCategoryViewSet)
router.register(r'product-subcategory', api_views.ProductSubCategoryViewSet)
router.register(r'subscription', api_views.SubscriptionViewSet)
router.register(r'subscription-type', api_views.SubscriptionTypeViewSet)
router.register(r'banner', api_views.BannerViewSet)
router.register(r'user', api_views.UserList)
router.register(r'notification', api_views.NotificationViewSet)
router.register(r'deliveryboy-notifications', api_views.DeliveryBoyNotificationsViewSet)
router.register(r'store-notifications', api_views.StoreNotificationsViewSet)
router.register(r'complain', api_views.ComplainViewSet)
router.register(r'storeareas', api_views.StoreAreasViewSet)
router.register(r'city', api_views.CityViewSet)
router.register(r'area', api_views.AreaViewSet)
router.register(r'subareas', api_views.SubAreaViewSet)
router.register(r'payment', api_views.OnlinePaymentViewSet)
router.register(r'recharge-history', api_views.RechargeHistoryViewSet)
router.register(r'cancelled-order', api_views.CancelledOrderViewSet)


urlpatterns = [
    path('reset_password/', auth_views.PasswordResetView.as_view(from_email="muhammadmeeran2003@gmail.com"), name ='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name ='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name ='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name ='password_reset_complete'),
    path('api/auth/login/', api_views.LoginView.as_view()),
    path('api/auth/register/', api_views.RegisterAPIView.as_view()),
    path('admin/', admin.site.urls),
    path('api/auth/logout/', LogoutView.as_view(), name='knox_logout'),
    path('api/', include(router.urls)),
    path('api/changePassword/', api_views.ChangePasswordView.as_view()),
    path('api/sendcode/', api_views.send_code),
    path('api/reset/', api_views.resetPass),
    path('api/checkcode/', api_views.checkCode),
    path('api/changepass/', api_views.changePass),
    path('jazz_cash/<int:amount>/<int:customerID>/', api_views.payment_view),
    path('payment_result/', api_views.payment_result_view),
    path('', home_page),

]

urlpatterns += path('web/', include(web_urls)),


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


