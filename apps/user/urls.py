from django.conf.urls import url
from django.contrib.auth.decorators import login_required
import user.views as views
from user.views import RegisterView,ActiveView,LoginView,UserInfoView,UserOrderView,AddressView,LogoutView
urlpatterns = [
    url(r'^register$',RegisterView.as_view(),name='register'),
    url(r'^active/(?P<token>.*)',ActiveView.as_view(),name='active'),
    url(r'^login$',LoginView.as_view(),name='login'),
    url(r'^order$',UserOrderView.as_view(),name='order'),
    url(r'^logout$',LogoutView.as_view(),name='logout'),    
    url(r'^$',UserInfoView.as_view(),name='user'),
    url(r'^address$',AddressView.as_view(),name='address')

]
app_name = "user"