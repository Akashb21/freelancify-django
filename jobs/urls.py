from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list_view, name='job_list'),
    path('post/', views.job_create_view, name='job_create'),
    path('<int:pk>/', views.job_detail_view, name='job_detail'),
    path('proposal/<int:proposal_id>/accept/', views.proposal_accept_view, name='proposal_accept'),
    
    # Project Showcase & Project Requests
    path('projects/', views.project_showcase_view, name='project_showcase'),
    path('projects/<int:pk>/', views.project_detail_view, name='project_detail'),
    path('request/send/<int:freelancer_id>/', views.create_project_request_view, name='create_project_request'),
    path('request/<int:pk>/status/', views.update_request_status_view, name='update_request_status'),
]
