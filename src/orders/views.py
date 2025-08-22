import datetime
import json

from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderProduct, Payment
from stores.models import Product

# Create your views here.


def place_order(request, total=0, quantity=0, cart_items=None):
    current_user = request.user
    grand_total = 0
    tax = 0
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("stores:shop")

    for cart_item in cart_items:
        total += cart_item.price * cart_item.quantity
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = tax + total

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]
            order.email = form.cleaned_data["email"]
            order.phone = form.cleaned_data["phone"]
            order.city = form.cleaned_data["city"]
            order.state = form.cleaned_data["state"]
            order.address_line_1 = form.cleaned_data["address_line_1"]
            order.address_line_2 = form.cleaned_data["address_line_2"]
            order.order_note = form.cleaned_data["order_note"]
            order.user = current_user
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get("REMOTE_ADDR")
            order.save()
            # generate order uniq number
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            dm = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr, dm, dt)
            current_date = d.strftime("%Y%d%m")
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()
            orderView = Order.objects.get(
                user=current_user, is_order=False, order_number=order_number
            )
            context = {
                "order": orderView,
                "cart_items": cart_items,
                "total": total, 
                "tax": tax,
                "grand_total": grand_total,
            }
            return render(request, "orders/payments.html", context)
    else:
        return redirect("carts:checkout")


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(
        user=request.user, is_order=False, order_number=body["orderID"]
    )
    # insert data into Payment table
    payment = Payment(
        user=request.user,
        payment_id=body["transID"],
        payment_method=body["payment_method"],
        amount_paid=order.order_total,
        status=body["status"],
    )
    payment.save()
    
    order.payment = payment
    order.is_order =True
    order.save()
    
    cart_items = CartItem.objects.filter(user=request.user)
    
    # insert data to OrderProduct Table
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id 
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        
        if item.product.discount_price:
            order_product.product_price = item.product.discount_price
        else:
            order_product.product_price = item.product.regular_price
            
        order_product.quantity = item.quantity
        order_product.ordered = True
        order_product.save()
        
        # set variation to OrderProduct table
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variation.set(product_variation)
        order_product.save()
        
        # reduce stock from product
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
        
    # clear cart
    CartItem.objects.filter(user=request.user).delete()

    # send receive email order
    subject = 'Thank you for you ordered'
    body = render_to_string('orders/receive_order_email.html',{
        'user':request.user,
        'order':order,
    })

    to_email = request.user.email
    send_email = EmailMessage(subject,body,to=[to_email,])
    send_email.send()

    data = {
        'order_number':order.order_number,
        'transID':payment.payment_id
    }
    return JsonResponse(data)

    


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID  = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number,is_order=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in order_products:
            subtotal += i.product_price * i.quantity
            
        payment = Payment.objects.get(payment_id=transID)
        context ={
            'order':order,
            'transId':payment.payment_id,
            'order_products':order_products,
            'payment':payment,
            'subtotal':subtotal
            
        }
        return render(request,'orders/order_complete.html',context)
    except:
        return redirect('home')    
    
