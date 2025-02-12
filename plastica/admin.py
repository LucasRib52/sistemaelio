from django.contrib import admin
from .models import (
    ProfissionalPlastica,
    ProcedimentosPlastica,
    RegistroAtendimentoPlastica,
    HistoricoProcedimentosPlastica,
    PreAgendamentoPlastica,
    ContratoPlastica,
    PagamentoContrato,
)

# Profissionais de Plástica
@admin.register(ProfissionalPlastica)
class ProfissionalPlasticaAdmin(admin.ModelAdmin):
    list_display = ("nome", "especialidade", "telefone", "email", "ativo", "created_at")
    list_filter = ("ativo", "especialidade", "created_at")
    search_fields = ("nome", "especialidade", "email", "telefone")
    ordering = ("nome",)
    list_per_page = 20


# Procedimentos de Plástica
@admin.register(ProcedimentosPlastica)
class ProcedimentosPlasticaAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco_base", "created_at")
    search_fields = ("nome",)
    ordering = ("nome",)
    list_per_page = 20


# Registro de Atendimento de Plástica
@admin.register(RegistroAtendimentoPlastica)
class RegistroAtendimentoPlasticaAdmin(admin.ModelAdmin):
    list_display = (
        "cliente",
        "procedimento",
        "profissional",
        "data",
        "valor_pago",
        "forma_pagamento",
        "status_pagamento",
    )
    list_filter = ("profissional", "data", "forma_pagamento")
    search_fields = ("cliente__name", "procedimento", "profissional__nome")
    ordering = ("-data",)
    list_per_page = 20
    readonly_fields = ("status_pagamento",)


# Histórico de Procedimentos de Plástica
@admin.register(HistoricoProcedimentosPlastica)
class HistoricoProcedimentosPlasticaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "procedimento", "profissional", "preco", "status_pagamento", "created_at")
    list_filter = ("procedimento", "created_at")
    search_fields = ("cliente__name", "procedimento")
    ordering = ("-created_at",)
    list_per_page = 20
    readonly_fields = ("status_pagamento",)


# Pré-Agendamentos de Plástica
@admin.register(PreAgendamentoPlastica)
class PreAgendamentoPlasticaAdmin(admin.ModelAdmin):
    list_display = ("nome", "celular", "procedimento", "data_agendamento", "posicao_agendamento", "cliente")
    list_filter = ("posicao_agendamento", "data_agendamento")
    search_fields = ("nome", "celular", "procedimento")
    ordering = ("-data_agendamento",)
    list_per_page = 20


# Contratos de Plástica
@admin.register(ContratoPlastica)
class ContratoPlasticaAdmin(admin.ModelAdmin):
    list_display = ("cliente", "procedimento", "valor_total", "data_contrato", "status")
    list_filter = ("status", "data_contrato")
    search_fields = ("cliente__name", "procedimento")
    ordering = ("-data_contrato",)
    list_per_page = 20
    readonly_fields = ("total_pago", "valor_faltante")


# Pagamentos de Contratos
@admin.register(PagamentoContrato)
class PagamentoContratoAdmin(admin.ModelAdmin):
    list_display = ("contrato", "valor", "data_pagamento")
    list_filter = ("data_pagamento",)
    search_fields = ("contrato__cliente__name",)
    ordering = ("-data_pagamento",)
    list_per_page = 20
