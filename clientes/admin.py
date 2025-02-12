from django.contrib import admin
from . import models


class RegistroClientesAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpf', 'telefone', 'email', 'created_at', 'updated_at',)
    search_fields = ('name', 'cpf', 'email',)


class HistoricoClientesAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'consulta_em', 'acao',)
    search_fields = ('cliente__name', 'acao',)  # Use cliente__name para busca no campo relacionado.


# Registro dos modelos no admin
admin.site.register(models.RegistroClientes, RegistroClientesAdmin)
admin.site.register(models.HistoricoClientes, HistoricoClientesAdmin)
