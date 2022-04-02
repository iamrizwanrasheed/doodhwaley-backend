from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from milkapp.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from operator import attrgetter
from django.http import JsonResponse
from .forms.product import ProductForm




@login_required(login_url='/web/login/')
def products_delete_view(request):
    if request.method == 'POST':
        # Delete A product
        ID = request.POST.get('id')
        if ID is not None:
            try:
                product_obj = Product.objects.get(id=ID)
                # product_obj.delete()
                messages.info(request,"Your Product Was Successfully Deleted")
            except Product.DoesNotExist:
                messages.error(request,"Please Enter A Valid ID")
        else:
            messages.error(request,"Please Enter A Valid ID")
    data = {"status":"Successfully Deleted"}
    return JsonResponse(data)


def getProductsQueryset(query=None):
	queryset = []
	queries = query.split(" ") # python install 2019 = [python, install, 2019]
	for q in queries:
		posts = Product.objects.filter(
				Q(name__icontains=q) | 
				Q(subcategory__name__icontains=q) |
				Q(subcategory__category__name__icontains=q) 
			).distinct()

		for post in posts:
			queryset.append(post)

	return list(set(queryset))


@login_required(login_url='/web/login/')
def products_view(request):
    context = {}
    products = Product.objects.all()

    # Add A Product
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()

	# Search
    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)
    products_list = sorted(getProductsQueryset(query), key=attrgetter('name')  ,reverse=True)    

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(products_list, 5)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context['products_list'] = products

    return render(request,'web/pages/Product/Products.html',context=context)


@login_required(login_url='/web/login/')
def add_product_view(request):
    context = {}
    # Add A Product
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()

    context['form'] = form

    return render(request,'web/pages/Product/AddProduct.html',context=context)