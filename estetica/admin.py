from django.contrib import admin
from .models import Profissional, Procedimentos, RegistroAtendimento, HistoricoProcedimentos, PreAgendamento

# Configuração para Profissionais
@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ("nome", "especialidade", "telefone", "email", "ativo", "created_at")
    list_filter = ("ativo", "especialidade", "created_at")
    search_fields = ("nome", "especialidade", "email", "telefone")
    ordering = ("nome",)
    list_per_page = 20


# Configuração para Procedimentos
@admin.register(Procedimentos)
class ProcedimentosAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco_base", "created_at")
    search_fields = ("nome",)
    ordering = ("nome",)
    list_per_page = 20


# Configuração para Registro de Atendimento
@admin.register(RegistroAtendimento)
class RegistroAtendimentoAdmin(admin.ModelAdmin):
    list_display = (
        "cliente",
        "procedimento",
        "profissional",
        "data",
        "valor_total",
        "valor_pago",
        "status_pagamento",
    )
    list_filter = ("profissional", "data", "forma_pagamento")
    search_fields = ("cliente__name", "procedimento__nome", "profissional__nome")
    ordering = ("-data",)
    list_per_page = 20
    readonly_fields = ("status_pagamento", "valor_faltante")


# Configuração para Histórico de Procedimentos
@admin.register(HistoricoProcedimentos)
class HistoricoProcedimentosAdmin(admin.ModelAdmin):
    list_display = ("cliente", "procedimento", "quantidade_sessoes", "preco", "status_pagamento", "created_at")
    list_filter = ("procedimento", "created_at")
    search_fields = ("cliente__name", "procedimento__nome")
    ordering = ("-created_at",)
    list_per_page = 20
    readonly_fields = ("status_pagamento", "valor_pago", "valor_faltante")


# Configuração para Pré-Agendamentos
@admin.register(PreAgendamento)
class PreAgendamentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "celular", "procedimento", "data_agendamento", "posicao_agendamento", "cliente")
    list_filter = ("posicao_agendamento", "data_agendamento")
    search_fields = ("nome", "celular", "procedimento__nome")
    ordering = ("-data_agendamento",)
    list_per_page = 20
