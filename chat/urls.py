from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('start/<str:username>/', views.start_conversation_view, name='start_conversation'),
    path('send/<int:conv_id>/', views.send_message_api, name='send_message_api'),
    path('fetch/<int:conv_id>/', views.fetch_messages_api, name='fetch_messages_api'),
]
