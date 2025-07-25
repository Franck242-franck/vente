from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentification : on indique explicitement le chemin du template
    path('login/', auth_views.LoginView.as_view(template_name='produits/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='produits/logout.html'), name='logout'),


    # Ton app produits
    path('', include('produits.urls')),
]
