from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _


# Create your models here.
class Category(models.Model):
    cat_name = models.CharField(_("category name"), max_length=50, unique=True)
    slug = models.SlugField(_("slug"), unique=True)
    cat_image = models.ImageField(_("category image"), upload_to="categories")

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
    def __str__(self):
        return self.cat_name

    def get_url(self):
        return reverse("stores:product_by_category", args=[self.slug])
    