from django.conf.urls import url
from goods.views import IndexView,DetailView,ListView
urlpatterns = [
url(r'^index$',IndexView.as_view(),name='index'),
url(r'^list/(?P<type_id>\d*)/(?P<page>\d*)$',ListView.as_view(),name='list'),
url(r'^goods/(?P<goods_id>\d+)$',DetailView.as_view(),name='detail')
]
app_name = "goods"