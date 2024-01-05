from rest_framework import serializers
from ...models import *
from django.contrib.auth import authenticate
from ...utlities.push import send_notification
from ...utlities.push_store import send_notification_store
from ...utlities.push_delivery_boy import send_notification_delivery_boy
from taggit.serializers import TagListSerializerField, TaggitSerializer
from rest_framework.renderers import JSONRenderer
from django.core import serializers as DJANGOSERIALIZER

User._meta.get_field("email")._unique = True


from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _("Your old password was entered incorrectly. Please enter it again.")
            )
        return value

    def validate(self, data):
        password_validation.validate_password(
            data["new_password"], self.context["request"].user
        )
        return data

    def save(self, **kwargs):
        password = self.validated_data["new_password"]
        user = self.context["request"].user
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "image",
            "phone",
            "address",
            "is_store",
            "is_customer",
            "is_deliveryBoy",
            "latitude",
            "longitude",
            "push_token",
            "is_verified",
            "first_name",
            "last_name",
        )


class StoreSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    area = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ("id", "user", "contract_image", "owner_name", "area")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class AreaSerializer(serializers.ModelSerializer):
    area_detail = CitySerializer(source="city", read_only=True)

    class Meta:
        model = Area
        fields = "__all__"


class SubAreaSerializer(serializers.ModelSerializer):
    area_detail = AreaSerializer(source="area", read_only=True)

    class Meta:
        model = SubArea
        fields = "__all__"


class DeliveryBoySerializer(serializers.ModelSerializer):
    user = UserSerializer()
    area = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = DeliveryBoy
        fields = [
            "user",
            "id",
            "status",
            "zone_latitude",
            "zone_longitude",
            "zone_address",
            "area",
        ]


class StoreAreaSerializer(serializers.ModelSerializer):
    store_detail = StoreSerializer(source="store_id", read_only=True)
    subarea_detail = SubAreaSerializer(source="sub_area", read_only=True)
    delivery_boy_detail = DeliveryBoySerializer(source="delivery_boy", read_only=True)

    class Meta:
        model = StoreAreas
        fields = "__all__"


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "image",
            "is_verified",
            "phone",
            "address",
            "is_store",
            "is_customer",
            "is_deliveryBoy",
            "latitude",
            "longitude",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password")


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    subarea_detail = SubAreaSerializer(source="subarea", read_only=True)
    subarea = serializers.SlugRelatedField(
        queryset=SubArea.objects.all(), slug_field="id"
    )

    class Meta:
        model = Customer
        fields = ["user", "id", "subarea", "subarea_detail", "balance"]


class ProductCategorySubCategoryField(serializers.RelatedField):
    def to_representation(self, value):
        return {"name": value.name, "id": value.id}


class ProductCategorySerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    subcategory = ProductCategorySubCategoryField(
        many=True, queryset=ProductSubCategory.objects.all()
    )

    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductSubCategorySerializer(TaggitSerializer, serializers.ModelSerializer):
    category_detail = ProductCategorySerializer(source="category", read_only=True)
    tags = TagListSerializerField()

    class Meta:
        model = ProductSubCategory
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    subcategory_detail = ProductSubCategorySerializer(
        source="subcategory", read_only=True
    )

    class Meta:
        model = Product
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    delivery_boy_detail = DeliveryBoySerializer(source="delivery_boy", read_only=True)
    store_detail = StoreSerializer(source="store", read_only=True)
    customer_detail = CustomerSerializer(source="customer", read_only=True)

    class Meta:
        model = Order
        fields = "__all__"

    def create(self, validated_data):
        customer = validated_data["customer"]
        temp_store, s_area = send_notification_store(customer, self)
        delivery_boy = send_notification_delivery_boy(customer, self, s_area)
        store = temp_store
        validated_data["store"] = store
        validated_data["delivery_boy"] = delivery_boy
        price = validated_data["price"]
        method = validated_data["payment_method"]
        if method == "JAZZ":
            if customer.balance < price:
                raise serializers.ValidationError(
                    _("You do not have enough balance in Your Wallet.")
                )
            else:
                customer.balance = customer.balance - price
                customer.save()
        return Order.objects.create(**validated_data)


class OrderProductSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source="product", read_only=True)

    class Meta:
        model = OrderProduct
        fields = "__all__"


class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    customer_detail = CustomerSerializer(source="customer", read_only=True)
    subscription_type_detail = SubscriptionTypeSerializer(
        source="subscription", read_only=True
    )
    product_detail = ProductSerializer(source="product_id", read_only=True)

    class Meta:
        model = Subscription
        fields = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class DeliveryBoyNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBoyNotifications
        fields = "__all__"


class StoreNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreNotifications
        fields = "__all__"


class ComplainSerializer(serializers.ModelSerializer):
    customer_detail = CustomerSerializer(source="customer", read_only=True)

    class Meta:
        model = Complain
        fields = "__all__"


class OnlinePaymentSerializer(serializers.ModelSerializer):
    customer_detail = CustomerSerializer(source="customer_id", read_only=True)

    class Meta:
        model = OnlinePayment
        fields = "__all__"


class RechargeHistorySerializer(serializers.ModelSerializer):
    payment_detail = OnlinePaymentSerializer(source="payment_id", read_only=True)

    class Meta:
        model = RechargeHistory
        fields = "__all__"


class CancelledOrderSerializer(serializers.ModelSerializer):
    order_detail = OrderSerializer(source="order", read_only=True)
    cancelled_by_detail = UserSerializer(source="cancelled_by", read_only=True)

    class Meta:
        model = CancelledOrder
        fields = "__all__"
