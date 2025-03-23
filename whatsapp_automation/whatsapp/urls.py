from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('media/', views.media_list, name='media_list'),
    path('api/messages/', views.api_messages, name='api_messages'),
    path('api/summary/', views.api_chat_summary, name='api_chat_summary'),
] 