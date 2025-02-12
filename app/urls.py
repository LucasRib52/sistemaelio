from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, dashboard

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página de login
    path('login/', CustomLoginView.as_view(), name='login'),

    # Logout
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Dashboard (após login)
    path('', dashboard, name='dashboard'),

    # Apps do sistema
    path('clientes/', include('clientes.urls')),
    path('estetica/', include('estetica.urls')),
    path('plastica/', include('plastica.urls')),
]
