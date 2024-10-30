from django.contrib import admin
from .models import *

# Registro de outros modelos
admin.site.register(Customer)
admin.site.register(ShippingAddress)
admin.site.register(Category)
admin.site.register(Payment)
admin.site.register(Address)

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

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')
    search_fields = ('product__name',)
    list_filter = ('product__category',)

# Configuração para o modelo Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date_ordered', 'complete', 'transaction_id')
    list_filter = ('complete', 'date_ordered')
    search_fields = ('transaction_id', 'customer__name')
    date_hierarchy = 'date_ordered'
    actions = ['mark_as_complete']

    def mark_as_complete(self, request, queryset):
        queryset.update(complete=True)
        self.message_user(request, f'{queryset.count()} pedidos foram marcados como completos.')
    mark_as_complete.short_description = 'Marcar pedidos selecionados como completos'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'date_added')
    search_fields = ('order__transaction_id', 'product__name')
    list_filter = ('date_added',)

