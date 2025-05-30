from django.contrib import admin

# Register your models here.



from django.contrib import admin
from .models import *



# Applicant Registration Admin


from django.contrib import admin
from .models import UserRegistration

class CustomUserAdmin(admin.ModelAdmin):  # 🔁 আগে ছিল UserAdmin, এখন admin.ModelAdmin

    model = UserRegistration

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

    list_display = (
        'full_name', 'id', 'role', 'roll_number', 'username', 'email',
        'mobile_number', 'intake', 'get_groups', 'position_no',
        'is_email_verified', 'is_active', 'is_staff', 'created_at',
    )

    list_filter = ('role', 'roll_number', 'intake', 'is_active', 'is_staff', 'groups')
    search_fields = ('full_name', 'email', 'roll_number', 'mobile_number')
    ordering = ('-created_at',)

admin.site.register(UserRegistration, CustomUserAdmin)
