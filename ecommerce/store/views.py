from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect


def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/store.html', context)

def product_detail(request, id_product):
    product = get_object_or_404(Product, id=id_product)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)

def checkout(request):
    context = {}
    return render(request, 'cart/checkout.html', context)

def get_cart(request):
    customer = request.user.customer  
    order, created = Order.objects.get_or_create(customer=customer, complete=False)  
    return order

def cart(request):
    cart = get_cart(request)
    order_items = cart.orderitem_set.all()
    print(f"Order Items: {order_items}")  # Adicione isso para depuração
    context = {
        'cart': cart,
        'order_items': order_items,
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        order = get_cart(request)  
        product = get_object_or_404(Product, id=product_id)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if not created:
            order_item.quantity += 1  
        order_item.save()  
        return redirect('cart')
    else:
        messages.error(request, "Você precisa estar logado para adicionar itens ao carrinho.")
        return render(request, 'cart/checkout.html')

