from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

'''
Each class represents a table in the database.
'''

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=200)

    def __str__(self):
        return self.name if self.name else "Cliente sem nome"

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    image_url = models.URLField(max_length=200, null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=True)
    delete_product = models.BooleanField(default=False, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
        return self.price
        return self.digital
        return self.delete_product

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        # Certifique-se de que os campos usados aqui não sejam None
        return f"Pedido {self.id} - {self.customer.name if self.customer else 'Cliente Desconhecido'} - {self.transaction_id or 'Sem transação'}"

    def get_total(self):
        order_items = OrderItem.objects.filter(order=self)
        total = sum([item.product.price * item.quantity for item in order_items])
        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

class Address(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="Brazil")

    def __str__(self):
        return f"{self.customer.username} - {self.street}, {self.city}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=100)
    amount = models.FloatField()
    date_paid = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.order.transaction_id}"

# Finalize order
@login_required
def finalize_order(request):
    customer = Customer.objects.get(user=request.user)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order_items = OrderItem.objects.filter(order=order)

    if request.method == "POST":
        order.complete = True
        order.save()
        # Clear the items in the cart (currently associated with the incomplete order)
        order_items.delete()
        return redirect('order_details', order_id=order.id)

    return render(request, 'finalize_order.html', {'order': order, 'items': order_items})

# Order details
@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'order_details.html', {'order': order, 'items': order_items})

# Add item to order (used to add to cart)
@login_required
def add_to_cart(request, product_id):
    customer = Customer.objects.get(user=request.user)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    product = get_object_or_404(Product, id=product_id)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    order_item.quantity += 1
    order_item.save()
    return redirect('cart')

# Shopping cart
@login_required
def cart(request):
    customer = Customer.objects.get(user=request.user)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'cart.html', {'order': order, 'items': order_items})

# Remove item from cart
@login_required
def remove_from_cart(request, product_id):
    customer = Customer.objects.get(user=request.user)
    order = get_object_or_404(Order, customer=customer, complete=False)
    product = get_object_or_404(Product, id=product_id)
    order_item = get_object_or_404(OrderItem, order=order, product=product)
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()
    return redirect('cart')
