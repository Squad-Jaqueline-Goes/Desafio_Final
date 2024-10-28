from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Category)
admin.site.register(Payment)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'digital', 'category')
    list_filter = ('digital', 'category')
    search_fields = ('name',)

    def delete_marked_products(self, request, queryset):
        products_to_delete = queryset.filter(digital=True)
        count = products_to_delete.count()
        products_to_delete.delete()
        self.message_user(request, f'{count} produtos foram deletados.')

# Registro do Stock com customização opcional para facilitar o gerenciamento
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')
    search_fields = ('product__name',)
    list_filter = ('product__category',)

# Registro do Order com customização opcional
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_ordered', 'complete', 'transaction_id')
    list_filter = ('complete', 'date_ordered')
    search_fields = ('transaction_id', 'customer__name')
    date_hierarchy = 'date_ordered'
