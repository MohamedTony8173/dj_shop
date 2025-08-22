from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AccountNew,UserProfile
from django.utils.html import format_html

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail_profile_pic(self,object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;"/>'.format(object.profile_pic.url))
    thumbnail_profile_pic.short_description ='Profile Image'
    
    list_display = ['thumbnail_profile_pic','user','city','state']


class AccountsAdminNew(UserAdmin):
    list_display = ["username", "email","date_join"]
    list_filter = ['username']
    filter_horizontal = ()
    filter_vertical = ()
    fieldsets = ()

admin.site.register(AccountNew, AccountsAdminNew)
admin.site.register(UserProfile,UserProfileAdmin)

# Register your models here.
