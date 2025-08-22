from django.contrib import admin
from .models import Product, Variation,RatingReview,ProductGallery
import admin_thumbnails




# Register your models here.
@admin_thumbnails.thumbnail('image')
class GalleryTabular(admin.TabularInline):
    model = ProductGallery
    extra =1

class ProductModelAdmin(admin.ModelAdmin):
    list_display = [
        "pro_name",
        "discount_price",
        "regular_price",
        "modify_at",
        "is_available",
        "stock",
    ]
    prepopulated_fields = {"slug": ("pro_name",)}
    inlines = [GalleryTabular]


class VariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'variation_category',
                    'variation_value', 'is_active']
    list_filter = ['product', 'variation_category',
                   'variation_value', 'is_active']
    list_editable = ['is_active']


admin.site.register(Product, ProductModelAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(RatingReview)
admin.site.register(ProductGallery)
