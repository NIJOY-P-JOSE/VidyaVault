from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/upload/', views.upload_project, name='upload_project'),
    path('projects/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('projects/<int:pk>/comment/', views.add_comment, name='add_comment'),
    
    # Profiles
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/', views.my_profile, name='my_profile'),
    
    # Admin/Faculty
    path('admin-review/', views.admin_review, name='admin_review'),
    path('projects/<int:pk>/score/', views.score_project, name='score_project'),
    
    # API endpoints for charts
    path('api/department-stats/', views.department_stats, name='department_stats'),
    path('api/tech-stats/', views.tech_stats, name='tech_stats'),
    path('api/user-skills/<str:username>/', views.user_skills, name='user_skills'),

    path('chatbot/<int:project_id>/', views.project_chatbot, name='project_chatbot'),
]
