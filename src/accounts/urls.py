from django.urls import path
from . import views
app_name = 'accounts'

urlpatterns = [
    path('register/',views.register_account,name='register'),
    path('login',views.login_view,name='login_account'),
    path('logout/',views.logout_account,name='logout_account'),
    path('active/<uidb64>/<token>/',views.active_account,name='active'),
    path('dashboard/',views.dashboard_account,name='dashboard_account'),
    path('forget-password/',views.forgot_password_account,name='forget_password_account'),
    path('send/link/',views.send_link_reset_password,name='send_link_reset'),
    path('reset/<uidb64>/<token>/',views.reset_password,name='reset_password'),
    path('reset_password_account/',views.reset_password_account,name='reset_password_account'),
    path('myorder/',views.my_order,name='my_order'),
    path('profile/',views.edit_profile,name='profile'),
    path('change_password/',views.change_password,name='change_password'),
    path('order_details/<int:order_id>/',views.order_details,name='order_details')
    
    
]
