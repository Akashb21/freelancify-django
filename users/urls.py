from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('freelancers/', views.freelancer_list_view, name='freelancer_list'),
    path('favorite/<int:freelancer_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/<str:username>/', views.profile_detail_view, name='profile_detail'),
]
