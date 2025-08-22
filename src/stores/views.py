from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from carts.models import CartItem
from carts.views import _cart_id
from categories.models import Category
from orders.models import OrderProduct
from stores.forms import RatingForm

from .models import Product, ProductGallery, RatingReview

# Create your views here.

def shop_store(request,category_slug=None):
    categories = None
    products = None

    
    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories,is_available=True)
        paginator = Paginator(products,3)
        page = request.GET.get('page')
        page_product = paginator.get_page(page)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products,3)
        page = request.GET.get('page')
        page_product = paginator.get_page(page)
        product_count = products.count()
        

    
    context = {
        'products':page_product,
        'product_count':product_count,
 
    }
    return render(request,'stores/shop.html',context)

def shop_product_detail(request,cat_slug,pro_slug):  
    try:
        product = Product.objects.get(category__slug=cat_slug,slug=pro_slug)
        in_cart = CartItem.objects.filter(product=product,cart__cart_id=_cart_id(request)).exists()
    except :
        pass
    
    try:
        order_product = OrderProduct.objects.filter(user_id=request.user.id,product_id=product.id).exists()
    except OrderProduct.DoesNotExist:
        order_product = None
        
    # calculate review 
    reviews = RatingReview.objects.filter(product__id=product.id,status=True)  
    
    # get product gallery
    product_gallery = ProductGallery.objects.filter(product_id=product.id)  
            
    context = {
        'product':product,
        'in_cart':in_cart,
        'order_product':order_product,
        'reviews':reviews,
        'product_gallery':product_gallery
    }
    return render(request,'stores/product_detail.html',context)


def shop_search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_at').filter(Q(descriptions__icontains=keyword) | Q(pro_name__icontains=keyword))
            product_count = products.count()

    context ={
        'products':products,
        'product_count':product_count,
    }
    return render(request,'stores/shop.html',context)
    
    
    
    
def product_list_min_max(request):
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')


    products = Product.objects.all()
    for product in products:
        if product.discount_price:
            if min_price:
                products = products.filter(discount_price__gte=min_price)
            if max_price:
                products = products.filter(discount_price__lte=max_price)
        else:
            if min_price:
                products = products.filter(regular_price__gte=min_price)
            if max_price:
                products = products.filter(regular_price__lte=max_price)  
        product_count = products.count()
              

    return render(request, 'stores/shop.html', {'products': products,'product_count':product_count,})
        
        
def submit_review_rating(request,product_id):
    if request.method == 'POST':
        url = request.META.get('HTTP_REFERER')
        
        try:
            review = RatingReview.objects.get(user__id=request.user.id,product__id=product_id)
            form = RatingForm(request.POST,instance=review)
            messages.success(request,'Thank , Your Review Has Been Updated')
            return redirect(url)
        except RatingReview.DoesNotExist:
            form = RatingForm(request.POST)
            if form.is_valid():
                data = RatingReview()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.product_id = product_id
                data.user_id = request.user.id 
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
            messages.success(request,'Thank , Your Review Has Been Submitted')
            return redirect(url)
    else:
        form = RatingForm()
        return redirect(url)    
          