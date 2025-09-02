# menu/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chef/$', consumers.ChefConsumer.as_asgi()),
    re_path(r'ws/customer/(?P<bill_id>\d+)/$', consumers.CustomerConsumer.as_asgi()), # Add this line
    # menu/routing.py
    re_path(r'ws/chef/(?P<restaurant_slug>[-\w]+)/$', consumers.ChefConsumer.as_asgi()),
]