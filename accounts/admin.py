from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import (
    Permission,
    Role,
    RolePermission,
    User,
    UserActivity,
    UserProfile,
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'display_name', 'description')
    ordering = ('name',)
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('name', 'display_name', 'description', 'is_active')}),
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'module', 'action', 'description', 'created_at')
    list_filter = ('module', 'action')
    search_fields = ('codename', 'description', 'module', 'action')
    ordering = ('module', 'action')
    readonly_fields = ('codename', 'created_at')


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission', 'created_at')
    list_filter = ('role', 'permission__module')
    search_fields = ('role__name', 'permission__codename')
    ordering = ('role',)
    autocomplete_fields = ('role', 'permission')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-created_at',)
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'branch', 'organization', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role', 'branch', 'organization')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    readonly_fields = ('id', 'last_login', 'date_joined', 'last_login_ip', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'first_name', 'last_name', 'phone', 'last_login_ip')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Organization'), {'fields': ('role', 'branch', 'organization')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'department', 'city', 'country', 'two_factor_enabled', 'theme_preference', 'updated_at')
    list_filter = ('two_factor_enabled', 'theme_preference', 'country', 'notification_email', 'notification_sms', 'notification_in_app')
    search_fields = ('user__email', 'user__username', 'title', 'department', 'city', 'country')
    ordering = ('user',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('user',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'user__username', 'action', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)
    readonly_fields = ('id', 'user', 'action', 'ip_address', 'user_agent', 'timestamp', 'details')
