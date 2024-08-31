from django.contrib import admin
from . models import User,Address

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display=['username','email','date_joined','is_verified', 'is_staff', 'is_active']
    readonly_fields = ('date_joined',)

admin.site.register(User,UserAdmin)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line', 'city', 'state', 'postal_code', 'country','phone_number','is_default')
    search_fields = ('user__username', 'address_line', 'city', 'state', 'postal_code', 'country')
    list_filter = ('state', 'country')


