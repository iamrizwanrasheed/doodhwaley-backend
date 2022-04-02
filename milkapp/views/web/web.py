from django.contrib.auth.decorators import login_required
from django.db.models import query
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import login,authenticate
from django.contrib import messages
from milkapp.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from operator import attrgetter
from django.http import JsonResponse
from .forms.customer import CustomerForm


def home_page(request):

    return render(request,'web/coming_soon.html')


@login_required(login_url='/web/login/')
def home_view(request):

    return render(request,'web/homepage.html')


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request=request,data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('/web/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request,'web/auth/login.html')



def getCustomersQueryset(query=None):
	queryset = []
	queries = query.split(" ") # python install 2019 = [python, install, 2019]
	for q in queries:
		posts = Customer.objects.filter(
				Q(user__username__icontains=q) | 
				Q(user__email__icontains=q) |
				Q(subarea__name__icontains=q) 
			).distinct()

		for post in posts:
			queryset.append(post)

	return list(set(queryset))



@login_required(login_url='/web/login/')
def customers_view(request):
    customers_list = Customer.objects.all()
    context={}

    # Add A Customer
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
	# Search
    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        print("Query is",query)
        context['query'] = str(query)
    customers_list = sorted(getCustomersQueryset(query), key=attrgetter('user.username')  ,reverse=True)    

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(customers_list, 5)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request,'web/pages/Customers/Customers.html',context={
        'customers_list' : users,
        'form' : form
        })




@login_required(login_url='/web/login/')
def customers_delete_view(request):
    if request.method == 'POST':
        # Delete A Customer
        ID = request.POST.get('id')
        if ID is not None:
            try:
                customer_obj = Customer.objects.get(id=ID)
                # customer_obj.delete()
                messages.info(request,"Your Customer Was Successfully Deleted")
            except Customer.DoesNotExist:
                messages.error(request,"Please Enter A Valid ID")
        else:
            messages.error(request,"Please Enter A Valid ID")
    data = {"status":"Successfully Deleted"}
    return JsonResponse(data)




@login_required(login_url='/web/login/')
def banners_view(request):
    context = {}
    banners = Banner.objects.all()
    context['banners'] = banners
    return render(request,'web/pages/Banners/banners.html',context=context)

