from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
import datetime
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Customer, Product, Category, Stock, Order, OrderItem, ShippingAddress, Address
from .forms import CustomUserCreationForm


def store(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category')

    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'query': query
    }
    return render(request, 'store/store.html', context)


def product_detail(request, id_product):
    product = get_object_or_404(Product, id=id_product)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)


@login_required
def cart(request):
    order = get_cart(request)
    order_items = order.orderitem_set.all() if order else []

    context = {
        'order': order,
        'items': order_items,
    }
    return render(request, 'cart/cart.html', context)


def get_cart(request):
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        return order
    return None


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        stock = Stock.objects.get(product=product)
        if stock.quantity <= 0:
            messages.error(request, "Produto fora de estoque.")
            return redirect('store')
    except Stock.DoesNotExist:
        messages.error(request, "Estoque não encontrado para este produto.")
        return redirect('store')

    customer, _ = Customer.objects.get_or_create(user=request.user, defaults={
        'name': request.user.username,
        'email': request.user.email,
    })

    order = get_cart(request)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if created:
        order_item.quantity = 1
    else:
        order_item.quantity += 1

    order_item.save()
    stock.decrease_stock(1)

    messages.success(request, f"{product.name} foi adicionado ao carrinho.")
    return redirect('cart')


@login_required
def remove_from_cart(request, product_id):
    order = get_cart(request)
    product = get_object_or_404(Product, id=product_id)

    try:
        order_item = OrderItem.objects.get(order=order, product=product)
        stock = Stock.objects.get(product=product)

        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order_item.delete()

        stock.increase_stock(1)
        messages.success(request, f"Quantidade de {product.name} reduzida ou item removido do carrinho.")
    except OrderItem.DoesNotExist:
        messages.error(request, "Esse item não está no seu carrinho.")
    except Stock.DoesNotExist:
        messages.error(request, "Estoque não encontrado para este produto.")

    return redirect('cart')


@login_required
def finalize_order(request):
    customer = Customer.objects.get(user=request.user)
    order = get_object_or_404(Order, customer=customer, complete=False)
    order_items = order.orderitem_set.all()

    if request.method == "POST":
        order.complete = True
        order.save()
        order_items.delete()  # Limpa o carrinho
        messages.success(request, "Pedido finalizado com sucesso!")
        return redirect('store')

    context = {'order': order, 'items': order_items}
    return render(request, 'cart/checkout.html', context)


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
            Customer.objects.create(user=user)
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
    return redirect('store')


def contact(request):
    return render(request, 'store/contact.html')
