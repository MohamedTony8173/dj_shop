from django.db import models
from django.utils.translation import gettext as _

from accounts.models import AccountNew
from stores.models import Product, Variation


# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(
        AccountNew, verbose_name=_("user"), on_delete=models.CASCADE
    )
    payment_id = models.CharField(_("payment id"), max_length=100)
    payment_method = models.CharField(_("payment method"), max_length=100)
    amount_paid = models.CharField(_("amount paid"), max_length=100)
    status = models.CharField(_("status"), max_length=100)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ("New", "New"),
        ("Accepted", "Accepted"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    )
    user = models.ForeignKey(
        AccountNew, verbose_name=_("user"), on_delete=models.CASCADE, null=True
    )
    payment = models.ForeignKey(
        Payment,
        verbose_name=_("payment"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    order_number = models.CharField(_("order number"), max_length=50)
    first_name = models.CharField(_("first name"), max_length=50)
    last_name = models.CharField(_("last name"), max_length=50)
    phone = models.CharField(_("phone"), max_length=50)
    email = models.EmailField(_("email"), max_length=254)
    address_line_1 = models.CharField(_("address line one"), max_length=50)
    address_line_2 = models.CharField(
        _("address line tow"), max_length=50, blank=True, null=True
    )
    city = models.CharField(_("city"), max_length=50)
    state = models.CharField(_("state"), max_length=50)
    order_note = models.CharField(_("order not"), max_length=100, null=True, blank=True)
    order_total = models.FloatField(_("order total"))
    tax = models.FloatField(_("tax"))
    status = models.CharField(_("status"), max_length=50, choices=STATUS, default="New")
    ip = models.CharField(_("ip"), max_length=50, blank=True, null=True)
    is_order = models.BooleanField(_("is order"), default=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_address(self):
        if self.address_line_2:
            return f"{self.address_line_1} {self.address_line_2}"
        else:
             return f"{self.address_line_1}"
            

    def __str__(self):
        return self.full_name()


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("order"), on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, verbose_name=_("payment"), on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        AccountNew, verbose_name=_("user"), on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, verbose_name=_("product"), on_delete=models.CASCADE
    )
    variation = models.ManyToManyField(
        Variation, verbose_name=_("Variation"), blank=True
    )
    quantity = models.IntegerField(_("quantity"))
    product_price = models.FloatField(_("product price"))
    ordered = models.BooleanField(_("ordered"), default=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.product.pro_name
