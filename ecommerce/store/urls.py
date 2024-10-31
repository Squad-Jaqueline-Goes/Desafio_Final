from django.urls import path
from store import views
from django.urls import include

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('finalize_order/', views.finalize_order, name='finalize_order'),
    path('contact/', views.contact, name='contact'),
    path('checkout/', views.checkout, name="checkout"),
    path('store/', views.store, name='store'),
    path('store/<int:id_product>/', views.product_detail, name="product_detail"),
<<<<<<< HEAD
=======
    path('register/', views.register, name='register'),
>>>>>>> dev
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),

]