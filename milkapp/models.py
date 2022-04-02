from django.db import models
from django.contrib.auth.models import AbstractUser
from .utlities.push import send_notification
import random
from taggit.managers import TaggableManager
from twilio.rest import Client
from django.conf import settings

client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)


class City(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class SubArea(models.Model):
    name = models.CharField(max_length=255)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class User(AbstractUser):
    image = models.ImageField(height_field=None, width_field=None, max_length=None)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    is_customer = models.BooleanField(default=False)
    is_store = models.BooleanField(default=False)
    is_deliveryBoy = models.BooleanField(default=False)
    push_token = models.CharField(max_length=200, default="")
    is_verified = models.BooleanField(default=False)
    reset_code = models.CharField(null=True, blank=True, max_length=6)

    def send_msg(self, to="+923044791344", from_="+17479980870", body="1234"):
        if self.is_customer:
            message = client.messages.create(to=to, from_=from_, body=body)

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            if self.is_customer:
                print("I am from here,", self)
                Customer.objects.create(user=self)
            elif self.is_store:
                Store.objects.create(user=self)
            elif self.is_deliveryBoy:
                DeliveryBoy.objects.create(user=self)


class PhoneVerify(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    verify_code = models.CharField(max_length=4, blank=True, null=True)

    def save(self, *args, **kwargs):
        created = not self.pk
        number = random.randint(1000, 9999)
        self.verify_code = number
        super().save(*args, **kwargs)
        if created:
            self.user_id.send_msg(body=number)

    def send(self):
        number = random.randint(1000, 9999)
        print("I am executed", number)
        self.verify_code = number
        super().save()
        self.user_id.send_msg(body=number)


# Create your models here.
class ProductCategory(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(height_field=None, width_field=None, max_length=None)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.name


class ProductSubCategory(models.Model):
    category = models.ForeignKey(
        ProductCategory, related_name="subcategory", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return "{}, {}".format(self.name, self.category.name)


class Product(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(height_field=None, width_field=None, max_length=None)
    side_image = models.ImageField(
        blank=True, height_field=None, width_field=None, max_length=None
    )
    back_image = models.ImageField(
        blank=True, height_field=None, width_field=None, max_length=None
    )
    price = models.IntegerField()
    description = models.TextField()
    discount = models.IntegerField()
    subcategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    featured = models.BooleanField(default=False)
    can_subscribe = models.BooleanField(default=False)
    quantity = models.CharField(max_length=10, default="1L")
    available_quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subarea = models.ForeignKey(
        SubArea, on_delete=models.CASCADE, blank=True, null=True
    )
    balance = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.user.username


class Store(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    owner_name = models.CharField(max_length=100, default="Meeran")
    contract_image = models.ImageField(
        height_field=None, width_field=None, max_length=None
    )

    def __str__(self):
        return self.user.username


class DeliveryBoy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(default="ACTIVE", max_length=50)
    zone_latitude = models.FloatField(blank=True, null=True)
    zone_longitude = models.FloatField(blank=True, null=True)
    zone_address = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username


class StoreAreas(models.Model):
    store_id = models.ForeignKey(Store, related_name="area", on_delete=models.CASCADE)
    delivery_boy = models.ForeignKey(
        DeliveryBoy,
        related_name="area",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    sub_area = models.OneToOneField(SubArea, on_delete=models.CASCADE)

    def __str__(self):
        return self.sub_area.name + ", " + self.store_id.user.username


class TimeSlot(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name


class Order(models.Model):
    choices = [
        ("CASH", "CASH"),
        ("JAZZ", "JAZZ CASH"),
        ("EASYPAISA", "EASYPAISA"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, default=1)
    delivery_boy = models.ForeignKey(DeliveryBoy, on_delete=models.CASCADE, default=1)
    price = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)
    user_complete = models.BooleanField(default=False)
    delivery_boy_complete = models.BooleanField(default=False)
    payment_method = models.CharField(choices=choices, max_length=10)
    time_slot = models.ForeignKey(
        TimeSlot, on_delete=models.CASCADE, null=True, blank=True
    )
    delivery = models.CharField(max_length=20, default="NEXT")


class OrderProduct(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="Product"
    )
    quantity = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        self.product.available_quantity = self.product.available_quantity - 1
        self.product.save()
        super().save(*args, **kwargs)  # Call the "real" save() method.


class SubscriptionType(models.Model):
    name = models.CharField(max_length=200)
    interval = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    choices = [
        ("CASH", "CASH"),
        ("JAZZ", "JAZZ CASH"),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=1)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    quantity = models.IntegerField(default=1)
    time_slot = models.ForeignKey(
        TimeSlot, on_delete=models.CASCADE, null=True, blank=True
    )
    price = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default="ACTIVE")
    subscription = models.ForeignKey(
        SubscriptionType, on_delete=models.CASCADE, default=0
    )
    last_delivered = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(choices=choices, max_length=10, default="CASH")


class Banner(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField()
    url = models.CharField(max_length=250, default="www.eazisols.com")


class Notification(models.Model):
    message = models.TextField()
    title = models.CharField(max_length=100)
    type_of = models.CharField(max_length=20, default="ALL")

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        Users = User.objects.all()
        if created:
            if self.type_of == "ALL":
                for user in Users:
                    if not user.push_token == "":
                        return send_notification(
                            user.push_token, self.title, self.message
                        )
            elif self.type_of == "RIDER":
                for user in Users.filter(is_deliveryBoy=True):
                    if not user.push_token == "":
                        return send_notification(
                            user.push_token, self.title, self.message
                        )
            elif self.type_of == "CUSTOMER":
                for user in Users.filter(is_customer=True):
                    if not user.push_token == "":
                        return send_notification(
                            user.push_token, self.title, self.message
                        )
            elif self.type_of == "STORE":
                for user in Users.filter(is_store=True):
                    if not user.push_token == "":
                        return send_notification(
                            user.push_token, self.title, self.message
                        )

    def __str__(self):
        return self.title


class Complain(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="This is a Simple Query")
    query = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    answer = models.TextField(null=True, blank=True)
    answered = models.BooleanField(default=False)


class DeliveryBoyNotifications(models.Model):
    message = models.TextField()
    title = models.CharField(max_length=100)
    delivery_boy = models.ForeignKey(DeliveryBoy, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        boy = DeliveryBoy.objects.get(id=self.delivery_boy.id).user
        if created:
            if not boy.push_token == "":
                return send_notification(boy.push_token, self.title, self.message)


class StoreNotifications(models.Model):
    message = models.TextField()
    title = models.CharField(max_length=100)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        store = Store.objects.get(id=self.store.id).user
        if created:
            if not store.push_token == "":
                return send_notification(store.push_token, self.title, self.message)


class OnlinePayment(models.Model):
    # status : success,pending
    status = models.CharField(max_length=20, null=True, blank=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.PROTECT)
    transaction_id = models.CharField(max_length=255)
    type_of = models.CharField(max_length=20, null=True, blank=True)
    amount = models.BigIntegerField(default=0)
    superhash = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


class RechargeHistory(models.Model):
    payment_id = models.ForeignKey(OnlinePayment, on_delete=models.PROTECT)
    customer_id = models.ForeignKey(Customer, on_delete=models.PROTECT)
    amount = models.BigIntegerField()
    date = models.DateTimeField(auto_now=True)


class CancelledOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cancelled_at = models.DateTimeField(auto_now=True)
    reason = models.TextField()
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(default="WAITING", null=False, blank=True, max_length=20)

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created:
            print("I am executed from cancel section")
            if self.order.customer.user != self.cancelled_by:
                send_notification(
                    self.order.customer.user.push_token,
                    "Order Cancelled",
                    "Your Order# {} Was Cancelled because {}".format(
                        self.order.id, self.reason
                    ),
                )
            if self.order.store.user != self.cancelled_by:
                print("I am exe from store section")
                StoreNotifications.objects.create(
                    message="Your Order# {} Was Cancelled because {}".format(
                        self.order.id, self.reason
                    ),
                    title="Order Cancelled",
                    store=self.order.store,
                )
            if self.order.delivery_boy.user != self.cancelled_by:
                print("I am exe from rider section")
                DeliveryBoyNotifications.objects.create(
                    message="Your Order# {} Was Cancelled because {}".format(
                        self.order.id, self.reason
                    ),
                    title="Order Cancelled",
                    delivery_boy=self.order.delivery_boy,
                )
