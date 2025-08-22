from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from carts.models import Cart, CartItem
from stores.models import Product, Variation
from django.contrib.auth.decorators import login_required
# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # ///////////////////// if user is authenticated /////////////////////////////////////////////////////////////////////////
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exist = CartItem.objects.filter(
            product=product, user=current_user).exists()
        if is_cart_item_exist:
            cartItem = CartItem.objects.filter(
                product=product, user=current_user)
            ex_var_cart = []
            id = []
            for item in cartItem:
                existing_variation = item.variations.all()
                ex_var_cart.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_cart:
                index = ex_var_cart.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                    if product.discount_price:
                        item.price = product.discount_price
                    else:
                        item.price = product.regular_price
                item.save()

        else:
            cartItem = CartItem.objects.create(
                product=product, user=current_user, quantity=1)
            if len(product_variation) > 0:
                cartItem.variations.clear()
                cartItem.variations.add(*product_variation)
            # check if there is discount price
            if product.discount_price:
                cartItem.price = product.discount_price
            else:
                cartItem.price = product.regular_price
            cartItem.save()
        return redirect("carts:cart_index")

# ///////////////////// if user not authenticated /////////////////////////////////////////////////////////////////////////
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(
                        product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        is_cart_item_exist = CartItem.objects.filter(
            product=product, cart=cart).exists()
        if is_cart_item_exist:
            cartItem = CartItem.objects.filter(product=product, cart=cart)
            ex_var_cart = []
            id = []
            for item in cartItem:
                existing_variation = item.variations.all()
                ex_var_cart.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_cart:
                index = ex_var_cart.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                    if product.discount_price:
                        item.price = product.discount_price
                    else:
                        item.price = product.regular_price
                item.save()

        else:
            cartItem = CartItem.objects.create(
                product=product, cart=cart, quantity=1)
            if len(product_variation) > 0:
                cartItem.variations.clear()
                cartItem.variations.add(*product_variation)
            # check if there is discount price
            if product.discount_price:
                cartItem.price = product.discount_price
            else:
                cartItem.price = product.regular_price
            cartItem.save()
        return redirect("carts:cart_index")


def index_cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    cart_items = None
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        grand_total = tax + total
    except:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, "cart/index.html", context)


def remove_from_cart(request, prod_id, cart_item_id):

    product = get_object_or_404(Product, id=prod_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('carts:cart_index')


def remove_item_cart(request, prod_id, cart_item_id):

    product = get_object_or_404(Product, id=prod_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except:
        pass
    return redirect('carts:cart_index')


@login_required(login_url=('accounts:login_account'))
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    cart_items = None
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.price * cart_item.quantity
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        grand_total = tax + total
    except:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'cart/checkout.html', context)
