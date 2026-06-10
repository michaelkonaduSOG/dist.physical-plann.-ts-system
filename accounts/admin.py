from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        'collector_id',
        'username',
        'phone',
        'role'
    )

    fields = (
        'username',
        'phone',
        'is_active'
    )

    readonly_fields = ('collector_id',)

    def save_model(self, request, obj, form, change):

        obj.role = "COLLECTOR"
        obj.save()

        raw = getattr(obj, "_raw_password", None)

        if raw:
            self.message_user(
                request,
                f"ID: {obj.collector_id} | Password: {raw}"
            )