from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'digital', 'delete_product')
    list_filter = ('digital', 'delete_product')
    search_fields = ('name',)

    def delete_marked_products(self, request, queryset):
        # Filtrar apenas os produtos marcados para exclusão
        products_to_delete = queryset.filter(delete_product=True)
        count = products_to_delete.count()
        products_to_delete.delete()
        self.message_user(request, f'{count} produtos foram deletados.')