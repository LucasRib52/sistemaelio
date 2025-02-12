from django.urls import path
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from . import views
from .views import ExportarClientesExcelView


urlpatterns = [
    path('clientes/list/', login_required(views.ClienteListView.as_view()), name='clientes_list'),
    path('clientes/create/', login_required(views.ClienteCreateView.as_view()), name='clientes_create'),
    path('clientes/exportar/', ExportarClientesExcelView.as_view(), name='exportar_clientes_excel'),
    path('clientes/editar/<int:pk>/', login_required(views.ClienteUpdateView.as_view()), name='cliente_edit'),
    path('clientes/excluir/<int:pk>/', login_required(views.ClienteDeleteView.as_view()), name='cliente_delete'),
    path('clientes/visualizar/<int:pk>/', login_required(views.ClienteDetailView.as_view()), name='cliente_view'),
]
