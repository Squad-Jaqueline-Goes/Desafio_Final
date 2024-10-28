from django.urls import path
from store import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),    
    path('checkout/', views.checkout, name="checkout"),
    path('store/', views.store, name='store'),
    path('store/<int:id_product>/', views.product_detail, name="product_detail"),
    path('store/search/', views.product_search, name='product_search'),

]