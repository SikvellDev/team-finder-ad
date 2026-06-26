from django.urls import path

from projects import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.project_list_view, name='project_list'),
    path('create-project/', views.project_create_view, name='project_create'),
    path('<int:project_id>/', views.project_detail_view,
         name='project_detail'),
    path('<int:project_id>/edit/', views.project_edit_view,
         name='project_edit'),
    path('<int:project_id>/complete/', views.complete_project_view,
         name='project_complete'),
    path('<int:project_id>/toggle-participate/',
         views.toggle_participate_view, name='toggle_participate'),
]
