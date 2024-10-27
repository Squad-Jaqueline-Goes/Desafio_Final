from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm
from .models import Address


def store(request):
    products = Product.objects.all()
    categories = Category.objects.all()  
    context = {'products': products, 'categories': categories}
    return render(request, 'store/store.html', context)

def product_detail(request, id_product):
    product = get_object_or_404(Product, id=id_product)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)

def product_search(request):
    query = request.GET.get('q') 
    products = Product.objects.all()

    if query:
        products = products.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(category__name__icontains=query)
        )

    return render(request, 'store/product_search.html', {'products': products})

def get_cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer  
        order, created = Order.objects.get_or_create(customer=customer, complete=False)  
    else:
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    return order

def cart(request):
    if request.user.is_authenticated:
        cart = get_cart(request)
        order_items = cart.orderitem_set.all()
    else:
        order_items = []
        cart = {'get_cart_total': 0, 'get_cart_items': 0} 

    context = {
        'cart': cart,
        'order_items': order_items,
    }
    return render(request, 'cart/cart.html', context)

def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user, defaults={
            'name': request.user.username,
            'email': request.user.email,
        })

        order = get_cart(request)  
        product = get_object_or_404(Product, id=product_id)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if created:
            order_item.quantity = 1  
        else:
            order_item.quantity += 1  
        order_item.save()  

        messages.success(request, f"{product.name} foi adicionado ao carrinho.")
        return redirect('cart')
    else:
        messages.error(request, "Você precisa estar logado para adicionar itens ao carrinho.")
        return render(request, 'cart/checkout.html')

def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        order = get_cart(request)  
        product = get_object_or_404(Product, id=product_id)
        
        try:
            order_item = OrderItem.objects.get(order=order, product=product)
            
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save() 
                messages.success(request, f"Quantidade de {product.name} reduzida. Agora você tem {order_item.quantity}.")
            else:
                order_item.delete()  
                messages.success(request, f"{product.name} foi removido do seu carrinho.")
                
        except OrderItem.DoesNotExist:
            messages.error(request, "Esse item não está no seu carrinho.")
        
        return redirect('cart')
    else:
        messages.error(request, "Você precisa estar logado para remover itens do carrinho.")
        return redirect('login')  

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was updated', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    else:
        print("User is not logged in")

    return JsonResponse('Payment submitted..', safe=False)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0} 

    context = {'items': items, 'order': order}
    return render(request, 'store/checkout.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Address.objects.create(
                customer=user,
                street=form.cleaned_data.get('street'),
                city=form.cleaned_data.get('city'),
                state=form.cleaned_data.get('state'),
                zipcode=form.cleaned_data.get('zipcode'),
                country=form.cleaned_data.get('country'),
            )
            login(request, user)
            return redirect('store')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bem-vindo, {username}!")
                return redirect('store')
            else:
                messages.error(request, 'Nome de usuário ou senha incorretos.')
        else:
            messages.error(request, 'Nome de usuário ou senha incorretos.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('store/store.html')