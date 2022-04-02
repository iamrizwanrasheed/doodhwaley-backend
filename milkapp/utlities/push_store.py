import requests 
import json
from milkapp.models import *
# defining the api-endpoint  



def send_notification_store(Customer,order):
    s_area = StoreAreas.objects.get(sub_area=Customer.subarea)
    our_store = s_area.store_id
    title = "A New Order Has Arrived"
    message = "Prepare an order for Customer : {0} \n\
    Address : {1} As Soon As Possible\n\
            ".format(Customer.user.username,Customer.user.address)
    StoreNotifications.objects.create(title=title,message=message,store=our_store)
    return our_store,s_area



def send_notification_store_subscription(Customer):
    s_area = StoreAreas.objects.get(sub_area=Customer.subarea)
    our_store = s_area.store_id
    title = "A New Order Has Arrived"
    message = "Prepare an order for Customer : {0} \n\
    Address : {1} As Soon As Possible\n\
            ".format(Customer.user.username,Customer.user.address)
    StoreNotifications.objects.create(title=title,message=message,store=our_store)
    return our_store,s_area