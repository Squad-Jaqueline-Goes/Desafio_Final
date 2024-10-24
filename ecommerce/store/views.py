from django.shortcuts import render
from .models import *
from django.shortcuts import render, get_object_or_404  

def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context)

def product_detail(request, id_product):
    product = get_object_or_404(Product, id=id_product)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)


def cart(request):
    context = {}
    return render(request, 'store/cart.html', context)

def checkout(request):
    context = {}
    return render(request, 'store/checkout.html', context)
