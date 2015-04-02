from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import admin_forms


User = get_user_model()


class UserAdmin(BaseUserAdmin):
    form = admin_forms.UserChangeForm
    add_form = admin_forms.UserCreationForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ('name', 'email')
    list_filter = ('is_active',)
    readonly_fields = ('date_joined',)
    search_fields = ('name', 'email')
    ordering = ('name',)


class VerifyUserAdmin(UserAdmin):
    readonly_fields = ('date_joined', 'email_verified')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(VerifyUserAdmin, self).get_fieldsets(request, obj)
        fieldsets_dict = OrderedDict(fieldsets)

        try:
            fields = list(fieldsets_dict['Permissions']['fields'])
        except KeyError:
            return fieldsets

        try:
            index = fields.index('is_active')
        except ValueError:
            # If get_fieldsets is called twice, 'is_active' will already be
            # removed and fieldsets will be correct so return it
            return fieldsets

        fields[index] = ('is_active', 'email_verified')
        fieldsets_dict['Permissions']['fields'] = tuple(fields)
        return tuple(fieldsets_dict.items())
