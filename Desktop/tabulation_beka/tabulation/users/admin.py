from django.contrib import admin
from .models import *
from .forms import *
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.login_form = AdminUsernameAuthenticationForm

# @admin.register(CustomUser)
class AccountAdmin(UserAdmin):
    list_display = ('email', 'date_joined', 'last_login', 'is_staff', )
    search_fields = ('email', )
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
            (
                None,
                {
                    'classes': ('wide',),
                    'fields': ('email','first_name', 'last_name','is_staff','is_superuser' ,'password1', 'password2'),
                },
            ),
        )
    
    def save_model(self, request, obj, form, change):
        if not obj.username:
            email_parts = obj.email.split('@')
            username = f"{email_parts[0]}"  
            obj.username = username


admin.site.site_header = 'Админ Панель'
admin.site.site_title = 'title'
admin.site.index_title = 'Табуляция Сайта'



