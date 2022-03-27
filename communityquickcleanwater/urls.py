from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib import admin
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage),
    path('contaminantsinformation/', views.information),
    path('monitoryourwater/', views.monitor),
    path('takecontaminanttest/', views.test),
    path('community/<name_of_community>', views.viewcommunity, name='community'),
    path('usersurvey/', views.usersurvey),
    path('log-in/', auth_views.LoginView.as_view(template_name="log_in.html")),
    path('sign-out/', auth_views.LogoutView.as_view(next_page="/")),
    path('sign-up/', views.sign_up),
    path('profile/', views.profile),
]
