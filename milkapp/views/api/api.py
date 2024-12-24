from django.http import request
from django.http.response import HttpResponse, JsonResponse
from milkapp.utlities.sms import send_msg
from django.shortcuts import render
from rest_framework.response import Response
from ...models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework import viewsets,serializers
from rest_framework import permissions
from rest_framework import status,filters
from rest_framework import generics
from ...permissions import IsAdminOrAuthenticatedReadOnly, IsAdminOrOwner, IsAdminOrReadOnly, IsOrderOwner, IsOwnerOrReadOnly,IsOwnerOrAdminOrReadOnly, IsUserOrAdminOrReadOnly
from knox.models import AuthToken
from django.contrib.auth import login
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from django.db.models import Q
from rest_framework.generics import UpdateAPIView
from rest_framework.authtoken.models import Token
from ...utlities.email import send_email,send_rejection,reset_mail
from datetime import timedelta,datetime,date
from rest_framework.decorators import api_view,renderer_classes,permission_classes
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib 
from django.contrib.auth.models import Group
import json
from rest_framework.pagination import PageNumberPagination

def create_sha256_signature(key, message):
    byte_key = key.encode('utf-8')
    message = message.encode('utf-8')
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest()



def payment_view(request,amount,customerID):
    if customerID is not None:
        customer = Customer.objects.get(id=customerID)
        pp_TxnDateTime = datetime.now().strftime('%Y%m%d%H%M%S')
        pp_TxnExpiryDateTime = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d%H%M%S')
        pp_TxnRefNo = 'T' + pp_TxnDateTime
        pp_ReturnURL = 'https://doodhwaley.com/payment_result/'
        pp_Version = '1.1'
        pp_Language = "EN"
        pp_TxnCurrency = "PKR"
        pp_BillReference = 'billRef'
        pp_BankID = 'TBANK'
        pp_Description = 'Description of transaction'
        pp_MerchantID = settings.JAZZ_MERCHANT_ID
        pp_Password =settings.JAZZ_PASSWORD
        pp_ProductID = "RETL"
        ppmpf_1 = '1'
        ppmpf_2 = '2'
        ppmpf_3 = '3'
        ppmpf_4 = '4'
        ppmpf_5 = '5'
        IntegrityHash = settings.JAZZ_INTEGRITY_SECRET
        hashString = IntegrityHash + '&'
        hashString += str(amount) + '&'
        hashString += pp_BankID + '&'
        hashString += pp_BillReference + '&'
        hashString += pp_Description + '&'
        hashString += pp_Language + '&'
        hashString += pp_MerchantID + '&'
        hashString += pp_Password + '&'
        hashString += pp_ProductID + '&'
        hashString += pp_ReturnURL + '&'
        hashString += pp_TxnCurrency + '&'
        hashString += pp_TxnDateTime + '&'
        hashString += pp_TxnExpiryDateTime + '&'
        hashString += pp_TxnRefNo + '&'
        hashString += pp_Version + '&'
        hashString += ppmpf_1 + '&'
        hashString += ppmpf_2 + '&'
        hashString += ppmpf_3 + '&'
        hashString += ppmpf_4 + '&'
        hashString += ppmpf_5
        superhash = create_sha256_signature(IntegrityHash,hashString)
        context = {
            "IntegrityHash" : IntegrityHash,
            "pp_MerchantID" : pp_MerchantID,
            "pp_Password" :pp_Password,
            'pp_TxnDateTime' : pp_TxnDateTime,
            'pp_TxnExpiryDateTime' : pp_TxnExpiryDateTime,
            'pp_TxnRefNo' : pp_TxnRefNo,
            'pp_Amount' : amount,
            'customer' : customer,
            'pp_ReturnURL' : pp_ReturnURL,
            'pp_Version' : pp_Version,
            'pp_Language' : pp_Language,
            'pp_TxnCurrency' : pp_TxnCurrency,
            'pp_ProductID' : pp_ProductID,
            'hashString' : superhash,
            'pp_Description' : pp_Description,
            'ppmpf_1' : ppmpf_1,
            'ppmpf_2' : ppmpf_2,
            'ppmpf_3' : ppmpf_3,
            'ppmpf_4' : ppmpf_4,
            'ppmpf_5' : ppmpf_5,
            'pp_BillReference' : pp_BillReference,
            'pp_BankID' : pp_BankID
        }
        OnlinePayment.objects.create(
            status="pending",
            superhash=superhash,
            amount=amount/100,
            transaction_id=pp_TxnRefNo,
            type_of="JAZZ",
            customer_id=Customer.objects.get(id=customerID)
            )
        return render(request,template_name='api/jazzcash.html',context=context)
    else:
        return HttpResponse("Invalid Request")

@csrf_exempt
def payment_result_view(request):
    if request.method == "POST":
        data = request.POST 
        response = data.get('pp_ResponseCode',None)
        transaction_id = data.get('pp_TxnRefNo',None)
        superhash = data.get('pp_SecureHash',None)
        amount = data.get('pp_Amount',None)
        merchantID = data.get('pp_MerchantID',None)
        pp_AuthCode = data.get('pp_AuthCode',None)
        pp_ResponseMessage = data.get('pp_ResponseMessage',None)
        

        if not None in [response,transaction_id,superhash,amount,merchantID]:
            context = {}
            if response is not None:
                if response == '000' :
                    context["status"] = 'success'
                elif response == '124':
                    context["status"] = 'failed'
                else:
                    context['status'] = 'error'
            obj = OnlinePayment.objects.get(transaction_id=transaction_id)
            obj.status = context["status"]
            obj.save()
            if context["status"] == 'success':
                RechargeHistory.objects.create(
                        amount=int(amount)/100,
                        customer_id= obj.customer_id,
                        payment_id = obj,
                    )
                customer = obj.customer_id
                customer.balance = customer.balance + int(amount)/100
                customer.save()
            context['type'] = pp_AuthCode
            context['transaction_id'] = transaction_id
            context['customer'] = obj.customer_id
            context['payment_id'] = obj.id
            context['amount'] = int(amount)/100
            context['responseMessage'] = pp_ResponseMessage
        return render(request,template_name='api/payment_result.html',context=context)
    
    return HttpResponse("Invalid Request")


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    queryset = ''
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # if using drf authtoken, create a new token 
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        token = AuthToken.objects.create(user)[1]
        # return new token
        return Response({'token': token}, status=status.HTTP_200_OK)





class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        myDict = dict(request.data)
        if serializer.is_valid():
            user = serializer.save()
            data = {}
            data["user"] = UserSerializer(user, context=self.get_serializer_context()).data
            data["token"] = AuthToken.objects.create(user)[1]
            if user.is_store:
                store = Store.objects.get(user=user)
                data["store"] = StoreSerializer(store, context=self.get_serializer_context()).data
            if user.is_customer:
                group = Group.objects.get(name='Customers')
                user.groups.add(group)
                user.save()
                customer = Customer.objects.get(user=user)
                customer.subarea = SubArea.objects.get(id=int(myDict["subarea"][0]))
                customer.save()
                data["customer"] = CustomerSerializer(customer, context=self.get_serializer_context()).data
            if user.is_deliveryBoy:
                deliveryBoy = DeliveryBoy.objects.get(user=user)
                data["deliveryBoy"] = DeliveryBoySerializer(deliveryBoy, context=self.get_serializer_context()).data
            user.save()
            if user.is_customer:
                number = random.randint(1000,9999)
                PhoneVerify.objects.create(user_id=user,verify_code=number)
            return Response(data)
        return Response(serializer.errors,status=402)


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, format=None):
        try:
            print("RIZWAN :: Received data:", request.data)  # See incoming data
            serializer = AuthTokenSerializer(data=request.data)
            if not serializer.is_valid():
                print("RIZWAN :: Validation errors:", serializer.errors)  # See validation errors
                return Response({
                    "error": "Invalid credentials", 
                    "details": serializer.errors
                }, status=400)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            login(request, user)
            return super(LoginView, self).post(request, format=None)
        except Exception as e:
            print("RIZWAN :: Error:", str(e))
            return Response({"error": str(e)}, status=400)

    def get_post_response_data(self, request, token, instance):
        UserSerializer2 = UserSerializer

        data = {
            'expiry': self.format_expiry_datetime(instance.expiry),
            'token': token,
        }
        if UserSerializer is not None:
            data["user"] = UserSerializer2(
                request.user,
                context=self.get_context()
            ).data
            if data["user"]['is_store']:
                store = Store.objects.get(user=data['user']['id'])
                data["store"] = StoreSerializer(store,context=self.get_context()).data
            if data["user"]['is_customer']:
                customer = Customer.objects.get(user=data['user']['id'])
                data["customer"] = CustomerSerializer(customer,context=self.get_context()).data
            if data["user"]['is_deliveryBoy']:
                deliveryBoy = DeliveryBoy.objects.get(user=data['user']['id'])
                data["deliveryBoy"] = DeliveryBoySerializer(deliveryBoy,context=self.get_context()).data
            if request.user.is_verified == False:
                obj,created = PhoneVerify.objects.get_or_create(user_id=request.user)
                if not created:
                    obj.send()
            if request.user.groups.filter(name = 'Admin').exists():
                data["is_admin"] = True
            if request.user.groups.filter(name = 'Customers').exists():
                data["is_customer"] = True
            if request.user.groups.filter(name = 'Stores').exists():
                data["is_store"] = True
            if request.user.groups.filter(name = 'Delivery Boys').exists():
                data["is_deliveryBoy"] = True
        return data

class UserList(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DeliveryBoyViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryBoySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DeliveryBoy.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = DeliveryBoy.objects.all().order_by("-id")
        store = self.request.query_params.get('store', None)
        storearea = self.request.query_params.get('storeareas', None)
        num = self.request.query_params.get('num', None)
        today = self.request.query_params.get('today',None)
        if today is not None:
            queryset = queryset.filter(user__date_joined__gte = datetime.now() - timedelta(days=1))
        if num is not None:
            queryset = queryset[:int(num)]
        if store is not None:
            queryset = queryset.filter(area__store_id=store)
        if storearea is not None:
            queryset = queryset.filter(area__isnull=True)
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if (request.user == instance.user) or request.user.groups.filter(name="Admin").exists():
            if 'userData' in request.data:
                user = instance.user
                user_serializer = UserSerializer(user,data=request.data,partial=partial)   
                if user_serializer.is_valid():
                    self.perform_update(user_serializer)
                    if getattr(instance, '_prefetched_objects_cache', None):
                        instance._prefetched_objects_cache = {}
                    return Response(user_serializer.data)
                return Response(user_serializer.errors)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                self.perform_update(serializer)
                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}
                return Response(serializer.data)
            return Response(serializer.errors)
        else:
            return Response({"message" : "Only Owner Can Update"},status=401)

class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Store.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Store.objects.all().order_by("-id")
        num = self.request.query_params.get('num', None)
        today = self.request.query_params.get('today',None)
        if today is not None:
            queryset = queryset.filter(user__date_joined__gte = datetime.now() - timedelta(days=1))
        if num is not None:
            queryset = queryset[:int(num)]
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if (request.user == instance.user) or request.user.groups.filter(name="Admin").exists():
            user = instance.user
            user_serializer = UserSerializer(user,data=request.data,partial=partial)   
            if user_serializer.is_valid():
                self.perform_update(user_serializer)
                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                if serializer.is_valid():
                    self.perform_update(serializer)
                    if getattr(instance, '_prefetched_objects_cache', None):
                        instance._prefetched_objects_cache = {}
                    return Response(serializer.data)
                return Response(serializer.errors)
            # incase updating user causes errors
            return Response(user_serializer.errors)
        else:
            return Response({"message" : "Only Owner Can Update"},status=401)

class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = City.objects.all()

class AreaViewSet(viewsets.ModelViewSet):
    serializer_class = AreaSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Area.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Area.objects.all()
        city_id = self.request.query_params.get('city_id', None)
        if city_id is not None:
            queryset = queryset.filter(city=city_id)
        return queryset

class SubAreaViewSet(viewsets.ModelViewSet):
    serializer_class = SubAreaSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = SubArea.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = SubArea.objects.all()
        area_id = self.request.query_params.get('area_id', None)
        if area_id is not None:
            queryset = queryset.filter(area=area_id)
        return queryset

class StoreAreasViewSet(viewsets.ModelViewSet):
    serializer_class = StoreAreaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = StoreAreas.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = StoreAreas.objects.all()
        store = self.request.query_params.get('store', None)
        deliveryboy = self.request.query_params.get('deliveryboy', None)
        if store is not None:
            queryset = queryset.filter(store_id=store)
        if deliveryboy is not None:
            queryset = queryset.filter(delivery_boy=deliveryboy)
        return queryset

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Customer.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Customer.objects.all().order_by("-id")
        if not self.request.user.groups.filter(name="Admin").exists():
            queryset = queryset.filter(user=self.request.user)
        num = self.request.query_params.get('num', None)
        today = self.request.query_params.get('today',None)
        subareas = self.request.query_params.get('subareas',None)

        if subareas is not None:
            subareas_list = subareas.split(',')
            queryset = queryset.filter(subarea__in=subareas_list)
            print(subareas_list)
                
        if today is not None:
            queryset = queryset.filter(user__date_joined__gte = datetime.now() - timedelta(days=1))
        if num is not None:
            queryset = queryset[:int(num)]
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if (request.user == instance.user) or request.user.groups.filter(name="Admin").exists():
            if 'verify_code' in request.data:
                obj = PhoneVerify.objects.get(user_id=instance.user)
                if obj.verify_code == request.data.get('verify_code'):
                    instance.user.is_verified = True
                    instance.user.save()
                    return Response(data=None,status=200)
                else:
                    return Response(data=None,status=401)
            if 'userData' in request.data:
                user = instance.user
                user_serializer = UserSerializer(user,data=request.data,partial=partial)   
                if user_serializer.is_valid():
                    self.perform_update(user_serializer)
                    if getattr(instance, '_prefetched_objects_cache', None):
                        instance._prefetched_objects_cache = {}
                    return Response(user_serializer.data)
                return Response(user_serializer.errors)

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                self.perform_update(serializer)
                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}
                return Response(serializer.data)
            return Response(serializer.errors)
        else:
            return Response({"message" : "Only Owner Can Update"},status=401)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated,IsOrderOwner]
    queryset = Order.objects.all().order_by('-id')

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Order.objects.all().order_by('-id')
        if self.request.user.groups.filter(name = 'Admin').exists():
            queryset = queryset
        # Write permissions are only allowed to the owner of the snippet.
        if self.request.user.is_customer:
            queryset = queryset.filter(customer__user=self.request.user)
        if self.request.user.is_store:
            queryset = queryset.filter(store__user=self.request.user)
        if self.request.user.is_deliveryBoy:
            queryset = queryset.filter(delivery_boy__user=self.request.user)
        customer = self.request.query_params.get('customer', None)
        deliveryBoy = self.request.query_params.get('deliveryBoy', None)
        status = self.request.query_params.get('status', None)
        store = self.request.query_params.get('store', None)
        exclude = self.request.query_params.get('exclude', None)
        monthly = self.request.query_params.get('monthly', None)

        month = self.request.query_params.get('month', None)
        weekly = self.request.query_params.get('week', None)
        manual = self.request.query_params.get('manual', None)
        today = self.request.query_params.get('today', None)
        yesterday = self.request.query_params.get('yesterday', None)
        recent = self.request.query_params.get('recent', None)

        if customer is not None:
            queryset = queryset.filter(customer=customer)
        if status is not None:
            if status == "ACTIVE":
                queryset=queryset.filter(Q(status="ACTIVE") |  Q(status="PICKED"))
            else:
                queryset = queryset.filter(status=status)
        if store is not None:
            queryset = queryset.filter(store=store)
        if deliveryBoy is not None:
            queryset = queryset.filter(delivery_boy=deliveryBoy)
        if exclude is not None:
            print(exclude)
            queryset = queryset.exclude(status=exclude)
        if monthly is not None:
            queryset = queryset.filter(Q(created_at__gte = datetime.now()-timedelta(days=1) - timedelta(days=30)))

        if weekly is not None:
            queryset = queryset.filter(created_at__date__week=date.today().isocalendar()[1])
        if today is not None:
            queryset = queryset.filter(created_at__date=date.today()-timedelta(days=1))
        if yesterday is not None:
            queryset = queryset.filter(created_at__date=(date.today()-timedelta(days=2)))
        if month is not None:
            queryset = queryset.filter(created_at__month=datetime.now().month)
        if recent is not None:
            queryset = queryset.order_by('-created_at')[:10]
        if manual is not None:
            start = self.request.query_params.get('start', None)
            start = datetime.fromtimestamp(int(float(start)))
            end = self.request.query_params.get('end', None)
            end = datetime.fromtimestamp(int(float(end)))
            queryset = queryset.filter(created_at__range=[start, end])
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if ('status' in request.data) and (request.data.get('status') == 'CANCELLED'):
            reason = request.data.get('reason',None)
            if reason is not None:
                CancelledOrder.objects.create(
                    order = instance,
                    reason=reason,
                    cancelled_by=request.user
                )
        if 'user_complete' in request.data:
            delivery_boy_complete = instance.delivery_boy_complete
            if request.data['user_complete'] == delivery_boy_complete:
                instance.status = "DELIVERED"    
        if 'delivery_boy_complete' in request.data:
            user_complete = instance.user_complete
            if request.data['delivery_boy_complete'] == user_complete:
                instance.status = "DELIVERED"
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class OrderProductViewSet(viewsets.ModelViewSet):
    serializer_class = OrderProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = OrderProduct.objects.all()

    def get_queryset(self):
        """
        Optionally restrict`s the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = OrderProduct.objects.all().order_by('-id')
        order_id = self.request.query_params.get('order_id', None)
        if order_id is not None:
            queryset = queryset.filter(order_id=order_id)
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    search_fields = ['name','subcategory__name']
    filter_backends = (filters.SearchFilter,)
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.all()


    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Product.objects.all()
        subcategory = self.request.query_params.get('subcategory', None)
        category = self.request.query_params.get('category', None)
        featured = self.request.query_params.get('featured', None)
        tag = self.request.query_params.get('tag', None)
        if subcategory is not None:
            queryset = queryset.filter(subcategory=subcategory)
        if category is not None:
            queryset = queryset.filter(subcategory__category=category)
        if featured is not None:
            queryset = queryset.order_by('-id').filter(featured=True)[:10]
        if tag is not None:
            queryset = queryset.order_by('-id').filter(tags__name__in=[tag])[:10]
        return queryset

class ProductCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = ProductCategory.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = ProductCategory.objects.all()
        order_id = self.request.query_params.get('order_id', None)
        tag = self.request.query_params.get('tag', None)
        if order_id is not None:
            queryset = queryset.filter(order_id=order_id)
        if tag is not None:
            queryset = queryset.order_by('-id').filter(tags__name__in=[tag])
        return queryset

class ProductSubCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSubCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = ProductSubCategory.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = ProductSubCategory.objects.all()
        category = self.request.query_params.get('category', None)
        tag = self.request.query_params.get('tag', None)
        if category is not None:
            queryset = queryset.filter(category=category)
        if tag is not None:
            queryset = queryset.order_by('-id').filter(tags__name__in=[tag])
        return queryset

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Subscription.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Subscription.objects.all()
        customer = self.request.query_params.get('customer', None)
        if customer is not None:
            queryset = queryset.filter(customer=customer)
        return queryset

class SubscriptionTypeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = SubscriptionType.objects.all()

class BannerViewSet(viewsets.ModelViewSet):
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Banner.objects.all()

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Notification.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Notification.objects.all().order_by('-id')
        return queryset

class DeliveryBoyNotificationsViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryBoyNotificationsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = DeliveryBoyNotifications.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = DeliveryBoyNotifications.objects.all().order_by('-id')
        deliveryBoy = self.request.query_params.get('deliveryBoy', None)
        exclude = self.request.query_params.get('exclude', None)
        if deliveryBoy is not None:
            queryset = queryset.filter(delivery_boy=deliveryBoy)
        if exclude is not None:
            queryset = queryset.exclude(status=exclude)
        return queryset

class StoreNotificationsViewSet(viewsets.ModelViewSet):
    serializer_class = StoreNotificationsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = StoreNotifications.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = StoreNotifications.objects.all().order_by('-id')
        store = self.request.query_params.get('store', None)
        exclude = self.request.query_params.get('exclude', None)
        if store is not None:
            queryset = queryset.filter(store=store)[:10]
        if exclude is not None:
            queryset = queryset.exclude(status=exclude)
        return queryset

class ComplainViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    serializer_class = ComplainSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Complain.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Complain.objects.all().order_by("-id")
        num = self.request.query_params.get('num', None)
        today = self.request.query_params.get('today',None)
        if today is not None:
            queryset = queryset.filter(Q(date__gte = datetime.now() - timedelta(days=1))&Q(answered=False))
        if num is not None:
            queryset = queryset[:int(num)]
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # print("The instance is ",instance)
        # print("Request data is ",request.data)
        if 'answer' in request.data:
            instance.answer = request.data['answer']
            send_email(instance)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class OnlinePaymentViewSet(viewsets.ModelViewSet):
    serializer_class = OnlinePaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    queryset = OnlinePayment.objects.all()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = OnlinePayment.objects.all().order_by("-id")
        if not self.request.user.groups.filter(name="Admin").exists():
            if self.request.user.is_customer:
                queryset = queryset.filter(customer_id__user=self.request.user)
            else:
                return Response({"message" : "Only Owner Can Update"},status=401)
        num = self.request.query_params.get('num', None)
        variant = self.request.query_params.get('variant',None)
        if variant is not None:
            queryset = queryset.filter(status=variant)
        if num is not None:
            queryset = queryset[:int(num)]
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if self.request.user.groups.filter(name="Admin").exists() or  self.request.user==instance.customer_id.user :

            if 'status' in request.data:
                instance.status = request.data['status']
                if instance.status == "rejected":
                    instance.save()
                    send_rejection(instance)
                elif instance.status == "success":
                    instance.save()
                    customer = instance.customer_id
                    customer.balance = customer.balance + instance.amount
                    customer.save()
                    RechargeHistory.objects.create(
                        amount=instance.amount,
                        customer_id= customer,
                        payment_id = instance,
                    )


            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            return Response({"message" : "Only Owner Can Update"},status=401)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class RechargeHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = RechargeHistorySerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrOwner]
    queryset = RechargeHistory.objects.all()



    def retrieve(self, request, *args, **kwargs):
        instance = request.user
        data = RechargeHistory.objects.order_by('-date').filter(customer_id=instance.customer)
        serializer = self.get_serializer(data,many=True)
        return Response(serializer.data)


class CancelledOrderViewSet(viewsets.ModelViewSet):
    serializer_class = CancelledOrderSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrOwner]
    queryset = CancelledOrder.objects.all()
    search_fields = [
                    'order__customer__user__username',
                    'order__store__user__username',
                    'order__delivery_boy__user__username',
                    'order__id'
                    ]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = CancelledOrder.objects.all().order_by("-id")
        user = self.request.query_params.get('user', None)
        today = self.request.query_params.get('today',None)
        monthly = self.request.query_params.get('monthly',None)
        weekly = self.request.query_params.get('weekly',None)
        status = self.request.query_params.get('status',None)
        type_of = self.request.query_params.get('type',None)

        if today is not None:
            queryset = queryset.filter(cancelled_at__date=date.today())
        if user is not None:
            queryset = queryset.filter(cancelled_by__id=int(user))
        if monthly is not None:
            queryset = queryset.filter(Q(cancelled_at__gte = datetime.now() - timedelta(days=30)))
        if weekly is not None:
            queryset = queryset.filter(cancelled_at__date__week=date.today().isocalendar()[1])
        if status is not None:
            queryset = queryset.filter(status=status)
        if type_of is not None:
            queryset = queryset.filter(order__payment_method=type_of)
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if 'status' in request.data:
            print(request.data['status'])
            if request.data['status'] == 'ACCEPT':
                instance.order.customer.balance = instance.order.customer.balance + instance.order.price
                instance.order.customer.save()
                print(instance.order.customer)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

# Basic DRF api view.
@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes((permissions.AllowAny,))
def send_code(request):
    print(request.user)
    obj,created = PhoneVerify.objects.get_or_create(user_id=request.user)
    if not created:
        obj.send()
    json_response = {"ok": True}
    return Response(json_response)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes((permissions.AllowAny,))
def resetPass(request):
    if request.method == 'POST':
        if 'email' in request.data:
            try:
                user = User.objects.get(email=request.data['email'])
                code = random.randint(1000,9999)
                user.reset_code = code
                user.save()
                reset_mail(code,user)
            except ObjectDoesNotExist:
                print('User Does Not exists')
    json_response = {"ok": True}
    return Response(json_response)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes((permissions.AllowAny,))
def checkCode(request):
    status= 401
    json_response = {}
    if request.method == 'POST':
        if 'email' in request.data:
            try:
                user = User.objects.get(email=request.data['email'])
                if 'code' in request.data:
                    if user.reset_code == request.data['code']:
                        status=200
                        json_response['ok'] = True
                    else:
                        json_response['ok'] = False
            except ObjectDoesNotExist:
                print('User Does Not exists')
    return Response(json_response,status=status)

@api_view(['POST'])
@renderer_classes([JSONRenderer])
@permission_classes((permissions.AllowAny,))
def changePass(request):
    status= 401
    json_response = {}
    if request.method == 'POST':
        if 'email' in request.data:
            try:
                user = User.objects.get(email=request.data['email'])
                if 'code' in request.data:
                    if user.reset_code == request.data['code']:
                        password = request.data['password']
                        if password is not None:
                            user.set_password(password)
                            user.save()
                            status=200
                            json_response['ok'] = True
                    else:
                        json_response['ok'] = False
            except ObjectDoesNotExist:
                print('User Does Not exists')
    return Response(json_response,status=status)
