import requests 
import json
from ..models import *
# defining the api-endpoint  



def send_notification_delivery_boy(Customer,order,s_area):
    our_rider = s_area.delivery_boy
    title = "A New Order Has Arrived"
    message = "Tomorrow,Take an order from \
            Store : {0} \n\
            Address : {1} As Soon As Possible\n\
            ".format(s_area.store_id.user.username,s_area.store_id.user.address)
    DeliveryBoyNotifications.objects.create(title=title,message=message,delivery_boy=our_rider)

    return our_rider



def send_notification_delivery_boy_subscription(Customer,order,s_area):
    our_rider = s_area.delivery_boy
    title = "A New Order Has Arrived"
    message = "Tomorrow,Take an order from \
            Store : {0} \n\
            Address : {1} As Soon As Possible\n\
            ".format(s_area.store_id.user.username,s_area.store_id.user.address)
    DeliveryBoyNotifications.objects.create(title=title,message=message,delivery_boy=our_rider)

    return our_rider
