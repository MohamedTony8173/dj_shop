from django.db import models
from django.utils.translation import gettext as _

from accounts.models import AccountNew
from stores.models import Product,Variation


# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(_("cart id"), max_length=50, blank=True)
    date_added = models.DateField(_("added at"), auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(AccountNew, verbose_name=_("user"), on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(
        Product, verbose_name=_("product"), on_delete=models.CASCADE
    )
    cart = models.ForeignKey(Cart, verbose_name=_("cart"), on_delete=models.CASCADE,null=True)
    variations = models.ManyToManyField(Variation, verbose_name=_("Variation"))
    quantity = models.IntegerField(_("quantity"))
    is_active = models.BooleanField(_("is active"), default=True)
    price = models.DecimalField(_("price"), max_digits=5, decimal_places=2,default=0.0)

    def __str__(self):
        return self.product.pro_name
    
    def sub_total(self):
        return self.price * self.quantity


            
                
            