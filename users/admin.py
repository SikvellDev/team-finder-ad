from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import Skill

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    """Кастомная админка для пользователя"""

    list_display = ['email', 'name', 'surname',
                    'phone', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'skills']
    search_fields = ['email', 'name', 'surname', 'phone']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {
            'fields': ('name', 'surname', 'avatar', 'phone',
                       'github_url', 'about', 'skills')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname',
                       'phone', 'password1', 'password2'),
        }),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Админка для навыков"""

    list_display = ['name', 'users_count']
    search_fields = ['name']
    ordering = ['name']

    @admin.display(description='Количество пользователей')
    def users_count(self, obj):
        return obj.users.count()
