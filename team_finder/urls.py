from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def redirect_to_projects(request):
    """Перенаправление с корневого пути на список проектов"""
    return redirect('projects:project_list')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_projects, name='home'),
    path('projects/', include('projects.urls')),
    path('users/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
