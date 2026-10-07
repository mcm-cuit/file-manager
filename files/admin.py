from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from files.models import User, File


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('文件管理权限', {'fields': ('is_developer',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('文件管理权限', {'fields': ('is_developer',)}),
    )
    list_display = ('username', 'github_id', 'is_developer', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_developer', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'github_id')


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'object_key', 'size', 'content_type', 'uploader_id', 'created_at')
    search_fields = ('original_name', 'object_key', 'uploader_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
