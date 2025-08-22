from django.urls import path
from . import views

app_name = "stores"

urlpatterns = [
    path('',views.shop_store,name='shop'),
    path('category/<slug:category_slug>/',views.shop_store,name='product_by_category'),
    path('category/<slug:cat_slug>/<slug:pro_slug>/',views.shop_product_detail,name='product_detail'),
    path('search/',views.shop_search,name='search'),
    path('min/max/',views.product_list_min_max,name='product_list_min_max'),
    path('reviews/<int:product_id>/',views.submit_review_rating,name='review_rating'),
    
    
    ]
