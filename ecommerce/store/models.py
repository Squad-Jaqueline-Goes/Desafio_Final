from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth.models import User

# Modelos

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

class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} em estoque"

    def increase_stock(self, amount):
        self.quantity += amount
        self.save()

    def decrease_stock(self, amount):
        if amount <= self.quantity:
            self.quantity -= amount
            self.save()
        else:
            raise ValueError("Quantidade insuficiente no estoque")

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    def get_total(self):
        """ Calcula o total do pedido somando os totais de todos os itens do pedido. """
        total = sum([item.get_total() for item in self.orderitem_set.all()])
        return total

    def get_cart_total(self):
        """ Um alias para get_total para clareza e consistência. """
        return self.get_total()

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Se o item for novo
            stock = Stock.objects.get(product=self.product)
            stock.decrease_stock(self.quantity)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Devolver o item ao estoque ao ser removido
        stock = Stock.objects.get(product=self.product)
        stock.increase_stock(self.quantity)
        super().delete(*args, **kwargs)

    def get_total(self):
        return self.quantity * self.product.price

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