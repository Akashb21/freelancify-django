from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.contract_list_view, name='contract_list'),
    path('<int:pk>/', views.contract_detail_view, name='contract_detail'),
    path('<int:pk>/submit-work/', views.submit_work_view, name='submit_work'),
    path('<int:pk>/approve-work/', views.approve_work_view, name='approve_work'),
    path('<int:pk>/review/', views.add_review_view, name='add_review'),
]
