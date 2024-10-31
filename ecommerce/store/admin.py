from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Category)
admin.site.register(Payment)
admin.site.register(Stock)

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