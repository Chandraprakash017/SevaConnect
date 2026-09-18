from django.urls import path
from . import views

urlpatterns = [
    path('parts/', views.list_parts, name='list_parts'),
    path('parts/create/', views.create_part, name='create_part'),
    path('parts/<str:part_id>/', views.get_part, name='get_part'),
    path('parts/<str:part_id>/update/', views.update_part, name='update_part'),
    path('parts/<str:part_id>/delete/', views.delete_part, name='delete_part'),
]
