import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct

from .forms import ProfileUserForm, RegistrationForm, UserForm
from .models import AccountNew, UserProfile

# Create your views here.


def register_account(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            phone_number = form.cleaned_data["phone_number"]
            user = AccountNew.objects.create_user(
                username=username, email=email, password=password
            )
            user.phone_number = phone_number
            user.save()

            # create user profile automatically
            profile = UserProfile()
            profile.user_id = user.id
            profile.save()

            # here to send email to user to activate his account
            subject = "activation an account"
            current_sit = get_current_site(request).domain
            body = render_to_string(
                "accounts/email_verify.html",
                {
                    "user": user,
                    "domain": current_sit,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_mail = EmailMessage(
                subject=subject,
                body=body,
                to=[
                    email,
                ],
                from_email=settings.EMAIL_HOST_USER,
            )
            to_mail.send()
            messages.success(request, "please check your An Account to Verify")
            return redirect("home")

    else:
        form = RegistrationForm()

    context = {"form": form}
    return render(request, "accounts/register.html", context)


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        remember = request.POST.get("remember_me")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exist:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variations = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variations.append(list(variation))

                        # to get access cart from user
                    cart_item = CartItem.objects.filter(user=user)
                    exist_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        exist_variation_list.append(list(existing_variation))
                        id.append(item.id)
                    for pro in product_variations:
                        if pro in exist_variation_list:
                            index = exist_variation_list.index(pro)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            login(request, user)
            # Set session expiry
            if not remember:
                request.session.set_expiry(0)  # Expires on browser close
            else:
                request.session.set_expiry(1209600)  # 2 weeks

            # messages.success(request,'You Are Logged In!')
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                if "next" in params:
                    next_page = params["next"]
                    return redirect(next_page)
            except:
                return redirect("accounts:dashboard_account")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("accounts:login_account")

    return render(request, "accounts/login.html")


@login_required(login_url="accounts:login_account")
def logout_account(request):
    user = request.user.is_authenticated
    if user:
        logout(request)
        return redirect("home")


def active_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = AccountNew._default_manager.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, "your account has been activated , please log in now "
        )
        return redirect("accounts:login_account")
    else:
        messages.error(request, "invalid link was given")
        return redirect("accounts:register")


@login_required(login_url="accounts:login_account")
def dashboard_account(request):
    order = Order.objects.order_by("-created_at").filter(
        user_id=request.user.id, is_order=True
    )
    order_count = order.count()
    context = {"order_count": order_count}
    return render(request, "accounts/dashboard.html", context)


def forgot_password_account(request):
    return render(request, "accounts/forget_password.html")


def send_link_reset_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        if AccountNew.objects.filter(email=email).exists():
            user = AccountNew.objects.get(email__exact=email)
            subject = "Reset Password"
            current_sit = get_current_site(request).domain
            body = render_to_string(
                "accounts/forgot_password_reset.html",
                {
                    "user": user,
                    "domain": current_sit,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_mail = EmailMessage(
                subject=subject,
                body=body,
                to=[
                    email,
                ],
                from_email=settings.EMAIL_HOST_USER,
            )
            to_mail.send()
            messages.success(request, "please check your An Account to reset password")
            return redirect("accounts:login_account")
        else:
            messages.error(request, "no account with this is email has found")
            return redirect("accounts:forget_password_account")


def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = AccountNew.objects.get(id=uid)
    except:
        pass
    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "now you can reset your password safely")
        return redirect("accounts:reset_password_account")
    else:
        messages.error(request, "wrong link not appropriate")
        return redirect("accounts:login_account")


def reset_password_account(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        user = AccountNew.objects.get(id=request.session["uid"])
        if password == confirm_password:
            user.set_password(password)
            user.save()
            messages.success(request, "successfully reset password , you can login now")
            return redirect("accounts:login_account")
        else:
            messages.error(request, "Not reset password , some think goes wrong")
            return redirect("accounts:reset_password_account")
    return render(request, "accounts/password_reset.html")


@login_required
def my_order(request):
    order = Order.objects.filter(user_id=request.user.id, is_order=True).order_by(
        "-created_at"
    )
    context = {"orders": order}
    return render(request, "accounts/myorder.html", context)


@login_required
def edit_profile(request):
    userProfile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        user_profile = ProfileUserForm(
            request.POST, request.FILES, instance=userProfile
        )
        if user_form.is_valid() and user_profile.is_valid():
            user_form.save()
            user_profile.save()
            messages.success(request, "successfully updated Profile")
            return redirect("accounts:profile")
    else:
        user_form = UserForm(instance=request.user)
        user_profile = ProfileUserForm(instance=userProfile)
    context = {
        "user_form": user_form,
        "user_profile": user_profile,
        "userProfile": userProfile,
    }
    return render(request, "accounts/edit_profile.html", context)


@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = AccountNew.objects.get(username__exact=request.user.username)
        if  new_password  and confirm_password :
            if new_password == confirm_password:
                success = user.check_password(current_password)
                if success:
                    user.set_password(new_password)
                    user.save()
                    messages.success(
                        request, "password has changed successfully ! login with it now"
                    )
                    logout(request)
                    return redirect("accounts:login_account")
                else:
                    messages.error(request, "password not match the current one")
                    return redirect("accounts:change_password")
            else:
                messages.error(request, "new password and confirm password does not match ")
                return redirect("accounts:change_password")
        else:
            messages.error(request, "please fill out all fields ")
            return redirect("accounts:change_password")
                

    return render(request, "accounts/change_password.html")



@login_required
def order_details(request,order_id):
    subtotal =0
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    for item in order_detail:
        subtotal += item.product_price * item.quantity
        
    context = {
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
    }
    return render(request,'accounts/order_details.html',context)