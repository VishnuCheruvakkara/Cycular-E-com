from django.contrib import admin
from . models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display=['username','email','date_joined','is_verified', 'is_staff', 'is_active']
    readonly_fields = ('date_joined',)

admin.site.register(User,UserAdmin)
