from django.contrib import admin

from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status',
                    'created_at', 'get_participants_count']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'owner__username', 'owner__email']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'owner', 'status')
        }),
        ('Ссылки и участники', {
            'fields': ('github_url', 'participants')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    @admin.display(description='Количество участников')
    def get_participants_count(self, obj):
        return obj.participants.count()
