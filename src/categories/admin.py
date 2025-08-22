from django.contrib import admin
from .models import Category
# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['cat_name']
    prepopulated_fields = {'slug':('cat_name',)}
    
