from django.urls import path
from . import views

urlpatterns = [
    path('ai/diagnose/', views.diagnose, name='ai_diagnose'),
    path('ai/chat/', views.chat, name='ai_chat'),
]
