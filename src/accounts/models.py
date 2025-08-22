from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext as _

# Create your models here.


class AccountManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError(_("email is required"))
        if not username:
            raise ValueError(_("username is required"))
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username=username, email=self.normalize_email(email), password=password
        )
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class AccountNew(AbstractBaseUser):
    username = models.CharField(_("username"), max_length=50, unique=True)
    email = models.EmailField(_("email"), max_length=254, unique=True)
    phone_number = models.CharField(_("phone"), max_length=50, null=True, blank=True)
    date_join = models.DateTimeField(_("join at"), auto_now_add=True)
    last_login = models.DateTimeField(_("join at"), auto_now_add=True)

    # field for permission
    is_active = models.BooleanField(_("is_active"), default=False)
    is_staff = models.BooleanField(_("is_staff"), default=False)
    is_admin = models.BooleanField(_("is_admin"), default=False)
    is_superadmin = models.BooleanField(_("is_superadmin"), default=False)

    objects = AccountManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def phone(self):
        if self.phone_number:
            return self.phone_number
        else:
            return "please consider to register phone number as possible as soon"


class UserProfile(models.Model):
    user = models.OneToOneField(
        AccountNew, verbose_name=_("user"), on_delete=models.CASCADE
    )
    address_line_1 = models.CharField(_("address 1"), max_length=150, blank=True)
    address_line_2 = models.CharField(_("address 2"), max_length=150, blank=True)
    phone = models.CharField(_("phone"), max_length=50,blank=True)
    city = models.CharField(_("city"), max_length=50, blank=True)
    state = models.CharField(_("state"), max_length=50, blank=True)
    profile_pic = models.ImageField(_("picture"), upload_to="userProfile", blank=True,default='default/user_default.png')
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at =models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.user.username

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"
