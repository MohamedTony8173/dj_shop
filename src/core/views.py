from django.shortcuts import render
from stores.models import Product
# Create your views here.

def index_store(request):
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products':products,
    }
    return render(request,'index.html',context)