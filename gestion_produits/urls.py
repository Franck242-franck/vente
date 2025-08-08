from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

# Import des vues JWT
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentification via interface HTML
    path('login/', auth_views.LoginView.as_view(template_name='produits/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='produits/logout.html'), name='logout'),

    # Authentification API (JWT)
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Routes de ton application "produits"
    path('', include('produits.urls')),
]
