from django.db import models
from django.utils.translation import gettext as _
from accounts.models import AccountNew
from categories.models import Category
from django.urls import reverse
from django.db.models import Avg,Count

# Create your models here.






# ////////////////////////////////////////////////////////class Ration Views //////////////////////////////////////////
class RatingReview(models.Model):
    product = models.ForeignKey(
        'Product', verbose_name=_("product"), on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        AccountNew, verbose_name=_("user"), on_delete=models.CASCADE
    )
    subject = models.CharField(_("subject"), max_length=50, null=True, blank=True)
    review = models.TextField(_("review"), max_length=500, null=True, blank=True)
    rating = models.FloatField(_("rating"))
    ip = models.CharField(_("ip"), max_length=50, null=True, blank=True)
    status = models.BooleanField(_("status"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    def __str__(self):
        return self.subject
    
    
    
# ////////////////////////////////////////////////////////class Product ////////////////////////////////////////// 
class Product(models.Model):
    pro_name = models.CharField(_("product name"), max_length=150, unique=True)
    slug = models.SlugField(_("slug"), unique=True)
    descriptions = models.TextField(_("descriptions"))
    discount_price = models.DecimalField(
        _("discount price"), max_digits=5, decimal_places=2, null=True, blank=True
    )
    regular_price = models.DecimalField(
        _("regular price"), max_digits=5, decimal_places=2
    )
    pro_image = models.ImageField(_("product image"), upload_to="products")
    stock = models.IntegerField(_("stock"))
    is_available = models.BooleanField(_("is available"), default=True)
    category = models.ForeignKey(
        Category, verbose_name=_("category"), on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    modify_at = models.DateTimeField(_("modified at"), auto_now=True)

    def __str__(self):
        return self.pro_name

    def get_url(self):
        return reverse("stores:product_detail", args=[self.category.slug, self.slug])
    
    # to get average of rating specific product
    def averageReview(self):
        review = RatingReview.objects.filter(product=self,status=True).aggregate(average=Avg('rating'))
        avg =0
        if review['average'] is not None:
            avg = float(review["average"])
        return avg    
    
    # to count how many has rating  specific product
    def countReview(self):
        review = RatingReview.objects.filter(product=self,status=True).aggregate(count=Count('id'))
        count =0
        if review['count'] is not None:
            count = int(review["count"])
        return count    
        


# ////////////////////////////////////////////////////////class Variation //////////////////////////////////////////
variation_category_choice = (
    ("color", "color"),
    ("size", "size"),
)


class VariationManager(models.Manager):
    def get_colors(self):
        return (
            super(VariationManager, self)
            .filter(variation_category="color", is_active=True)
            .order_by("variation_value")
        )

    def get_size(self):
        return (
            super(VariationManager, self)
            .filter(variation_category="size", is_active=True)
            .order_by("variation_value")
        )


class Variation(models.Model):
    product = models.ForeignKey(
        Product, verbose_name=_("product"), on_delete=models.CASCADE
    )
    variation_category = models.CharField(
        _("variation category"), max_length=100, choices=variation_category_choice
    )
    variation_value = models.CharField(_("variation value"), max_length=100)
    is_active = models.BooleanField(_("is_active"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    objects = VariationManager()

    def __str__(self):
        return self.variation_value

# product gallery
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.CASCADE)
    image = models.ImageField(_("image"), upload_to='product/gallery')