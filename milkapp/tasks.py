import string

from .utlities.push_delivery_boy import send_notification_delivery_boy_subscription
from .utlities.push_store import send_notification_store_subscription
from .models import *

from celery import shared_task
from datetime import datetime, date,timezone


def checkCustomer(Customer,price):
    if (Customer.balance-price) < 0:
        return 'CASH'
    Customer.balance = Customer.balance - price
    Customer.save()
    return 'JAZZ'

@shared_task
def my_task():
    queryset = Subscription.objects.filter(status="ACTIVE")
    for obj in queryset:
        if obj.subscription.interval == 1:
            customer = obj.customer
            check = checkCustomer(customer,obj.price)
            temp_store,s_area = send_notification_store_subscription(customer)
            delivery_boy = send_notification_delivery_boy_subscription(customer,obj,s_area)
            order_store = temp_store
            order_delivery_boy = delivery_boy
            order_id = Order.objects.create(
                customer=obj.customer,
                store=order_store,
                delivery_boy=order_delivery_boy,
                price=obj.price,
                time_slot=obj.time_slot,
                payment_method=check)
            OrderProduct.objects.create(order_id=order_id,product=obj.product_id,quantity=obj.quantity)

        else:
            d0 = obj.last_delivered
            print("I am alternate days")
            d1 = datetime.now(timezone.utc)
            delta = (d1-d0).days
            print("Days difference is : ",delta)
            if (delta % obj.subscription.interval == 0) :
                check = checkCustomer(customer,obj.price)
                temp_store,s_area = send_notification_store_subscription(customer)
                delivery_boy = send_notification_delivery_boy_subscription(customer,obj,s_area)
                order_store = temp_store
                order_delivery_boy = delivery_boy
                obj.last_delivered = d1
                obj.save()
                order_id = Order.objects.create(
                    customer=obj.customer,
                    store=order_store,
                    delivery_boy=order_delivery_boy,
                    price=obj.price,
                    time_slot=obj.time_slot,
                    payment_method=check)
                OrderProduct.objects.create(order_id=order_id,product=obj.product_id,quantity=obj.quantity)


@shared_task
def my_task2():
    print("I am executed for the first time")


