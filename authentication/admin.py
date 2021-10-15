from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Register your models here.


class CustomUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Fields', {'fields': ('uid', 'name', 'photoUrl',), },),)
    add_fieldsets = (
        (None, {'fields': ('uid', 'username', 'password1', 'password2',), },),)
    list_display = ('uid', 'username', 'email', 'name',)
    search_fields = ('uid', 'email',)


admin.site.register(User, CustomUserAdmin)
