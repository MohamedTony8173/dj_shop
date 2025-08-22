from django.contrib import admin
from .models import Order,OrderProduct,Payment


class InlineOrderProduct(admin.TabularInline):
        model = OrderProduct
        extra = 0
        readonly_fields = ['payment','order','quantity','product_price','user','product','variation','ordered']
    
class OrderAdmin(admin.ModelAdmin):
    # |naturaltime
    list_display = ['full_name','phone','email','city','order_total','is_order']
    list_filter = ['status','is_order']
    search_fields = ['order_number','full_name','email','phone']
    list_per_page = 15
    inlines =[ InlineOrderProduct,]
    

# Register your models here.
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Payment)