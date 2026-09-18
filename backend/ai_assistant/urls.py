from django.urls import path
from . import views

urlpatterns = [
    path('ai/diagnose/', views.diagnose, name='ai_diagnose'),
    path('ai/followup/', views.followup, name='ai_followup'),
    path('ai/session/<str:session_id>/', views.get_diagnosis_session, name='ai_session'),
    path('ai/chat/', views.chat, name='ai_chat'),
]
