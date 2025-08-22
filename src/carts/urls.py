from django.urls import path 
from . import views

app_name='carts'

urlpatterns = [
    path('',views.index_cart,name='cart_index'),
    path('add-cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('remove-cart/<int:prod_id>/<int:cart_item_id>/',views.remove_from_cart,name='remove_from_cart'),
    path('remove-cart-item/<int:prod_id>/<int:cart_item_id>/',views.remove_item_cart,name='remove_item_cart'),
    path('checkout/',views.checkout,name='checkout')
]
