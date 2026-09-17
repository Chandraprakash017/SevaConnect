from django.urls import path
from . import views

urlpatterns = [
    path('departments/', views.list_departments, name='list_departments'),
    path('departments/<str:dept_id>/', views.get_department, name='get_department'),
    path('departments/create/', views.create_department, name='create_department'),
    path('departments/<str:dept_id>/update/', views.update_department, name='update_department'),
    path('departments/<str:dept_id>/delete/', views.delete_department, name='delete_department'),
]
