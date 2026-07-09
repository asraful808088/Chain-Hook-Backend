from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Client, UserActivityLog



class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for User model
    """
    
    list_display = [
        'id', 'email', 'name', 'is_active', 'is_staff', 'is_admin', 
        'create_date_time'
    ]
    
    list_filter = [
        'is_active', 'is_staff', 'is_admin', 
        'create_date_time', 'update_date_time'
    ]
    
    search_fields = ['email', 'name']
    ordering = ['-create_date_time']
    readonly_fields = ['create_date_time', 'update_date_time']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions')
        }),
        (_('Important Dates'), {'fields': ('create_date_time', 'update_date_time')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
    


class ClientAdmin(admin.ModelAdmin):
    """
    Admin configuration for Client model with boolean fields
    """
    
    list_display = [
        'id',
        'user', 
        'name', 
        'api_key', 
        'base_url',
        'for_login',
        'for_payment',
        'is_active', 
        'create_date_time'
    ]
    
    list_filter = [
        'for_login',
        'for_payment',
        'is_active', 
        'create_date_time',
        'update_date_time'
    ]
    
    search_fields = [
        'user__email', 
        'user__name', 
        'name', 
        'base_url', 
        'api_key'
    ]
    
    readonly_fields = ['create_date_time', 'update_date_time', 'api_key']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'base_url')
        }),
        ('API Key', {
            'fields': ('api_key',),
            'classes': ('wide',),
        }),
        ('Permissions', {
            'fields': ('for_login', 'for_payment', 'is_active'),
            'description': 'Define what this client can access'
        }),
        ('Timestamps', {
            'fields': ('create_date_time', 'update_date_time'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['regenerate_api_keys']
    
    def regenerate_api_keys(self, request, queryset):
        for client in queryset:
            client.regenerate_api_key()
        self.message_user(
            request, 
            f'Successfully regenerated API keys for {queryset.count()} clients.'
        )
    regenerate_api_keys.short_description = "Regenerate API keys for selected clients"
    
    def for_login_display(self, obj):
        return "✅" if obj.for_login else "❌"
    for_login_display.short_description = "Login"
    
    def for_payment_display(self, obj):
        return "✅" if obj.for_payment else "❌"
    for_payment_display.short_description = "Payment"



class UserActivityLogAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserActivityLog
    """
    
    list_display = ['user', 'action', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__email', 'user__name']
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False




admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(UserActivityLog, UserActivityLogAdmin)