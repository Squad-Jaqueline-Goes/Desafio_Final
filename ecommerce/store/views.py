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
import stripe
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm


# Inicializa a chave secreta do Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

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
@login_required
def finalize_order(request):
    customer = Customer.objects.get(user=request.user)
    order = get_object_or_404(Order, customer=customer, complete=False)
    order_items = order.orderitem_set.all()

    if request.method == "POST":
        # Obtém o token de pagamento do Stripe enviado pelo formulário
        token = request.POST.get('STRIPE_SECRET_KEY')

        # Verifique se o token foi recebido
        if not token:
            messages.error(request, "Erro no pagamento: token não encontrado.")
            return redirect('checkout')

        # Calcula o valor do pedido em centavos
        amount = int(order.get_cart_total() * 100)  # Em centavos para o Stripe

        try:
            # Cria uma cobrança no Stripe
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                description=f"Pedido #{order.id}",
                source=token  # O token é usado aqui como source
            )

            # Se o pagamento for bem-sucedido, finalize o pedido
            order.complete = True
            order.save()
            order_items.delete()  # Limpa o carrinho após a conclusão
            messages.success(request, "Pedido finalizado com sucesso e pagamento realizado!")
            return redirect('store')
        except stripe.error.CardError as e:
            messages.error(request, f"Erro no pagamento: {str(e)}")
            return redirect('checkout')

    context = {
        'order': order,
        'items': order_items,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'cart/checkout.html', context)


def checkout(request):
    if request.user.is_authenticated:
        # Verifica ou cria um cliente associado ao usuário autenticado
        customer, created = Customer.objects.get_or_create(user=request.user)

        # Pega o pedido ou cria um novo se não houver um incompleto
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Itens do pedido
        items = order.orderitem_set.all()

        # Calcule o total de itens e o total do pedido
        total_items = sum(item.quantity for item in items)
        total_price = sum(item.product.price * item.quantity for item in items)
    else:
        items = []
        total_items = 0
        total_price = 0

    context = {
        'items': items,
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'total_items': total_items,
        'total_price': total_price,
    }
    return render(request, 'store/checkout.html', context)


def create_checkout_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = data.get('order_id')

        try:
            # Recupera o pedido
            order = Order.objects.get(id=order_id, complete=False)
            amount = int(order.get_cart_total() * 100)  # Valor em centavos

            # Cria a sessão de pagamento
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'brl',
                        'product_data': {
                            'name': f'Pedido #{order.id}',
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/checkout/'),
            )

            return JsonResponse({'sessionId': session.id})

        except Order.DoesNotExist:
            return JsonResponse({'error': 'Pedido não encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


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
