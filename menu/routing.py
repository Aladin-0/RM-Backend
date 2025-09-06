# menu/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chef/$', consumers.ChefConsumer.as_asgi()),
    re_path(r'ws/customer/(?P<bill_id>\d+)/$', consumers.CustomerConsumer.as_asgi()),
    re_path(r'ws/chef/(?P<restaurant_slug>[-\w]+)/$', consumers.ChefConsumer.as_asgi()),
    re_path(r'ws/cashier/(?P<restaurant_slug>[-\w]+)/$', consumers.CashierConsumer.as_asgi()),
]