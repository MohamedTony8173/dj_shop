from django.urls import path
from . import views
app_name = 'orders'

urlpatterns = [
    path('place_order', views.place_order, name='place_order'),
    path('payment/',views.payments,name='payment'),
    path('complete/',views.order_complete,name='complete')
]
