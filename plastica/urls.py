from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    ProfissionalPlasticaCreateView,
    ProfissionalPlasticaListView,
    ProfissionalPlasticaUpdateView,
    ProfissionalPlasticaDeleteView,
    ProcedimentoPlasticaCreateView,
    ProcedimentoPlasticaListView,
    ProcedimentoPlasticaUpdateView,
    ProcedimentoPlasticaDeleteView,
    RegistroAtendimentoPlasticaCreateView,
    HistoricoAtendimentosPlasticaListView,
    AtendimentoPlasticaUpdateView,
    AtendimentoPlasticaDeleteView,
    ClienteAutocompletePlasticaView,
    PreAgendamentoPlasticaCreateView,
    PreAgendamentoPlasticaListView,
    PreAgendamentoPlasticaUpdateView,
    PreAgendamentoPlasticaDeleteView,
    PreAgendamentoPlasticaUpdateStatusView,
    PreAgendamentoPlasticaCalendarView,
    PreAgendamentoPlasticaUpdateEventView,
    ContratoPlasticaCreateView,
    ContratoPlasticaListView,
    ContratoPlasticaUpdateView,
    ContratoPlasticaDeleteView,
    PagamentoContratoCreateView,
    HistoricoPagamentosView,
    PagamentoUpdateView,
    RelatorioFinanceiroPlasticaView,
    RelatorioFinanceiroContratoView,
    ExportarAtendimentosPlasticaExcelView,
    ExportarContratosPlasticaExcelView,
)

urlpatterns = [
    # Profissionais de Plástica
    path('plastica/profissional/cadastrar/', login_required(ProfissionalPlasticaCreateView.as_view()), name='profissional_plastica_create'),
    path('plastica/profissional/lista/', login_required(ProfissionalPlasticaListView.as_view()), name='profissional_plastica_list'),
    path('plastica/profissional/editar/<int:pk>/', login_required(ProfissionalPlasticaUpdateView.as_view()), name='profissional_plastica_update'),
    path('plastica/profissional/excluir/<int:pk>/', login_required(ProfissionalPlasticaDeleteView.as_view()), name='profissional_plastica_delete'),

    # Procedimentos de Plástica
    path('plastica/procedimento/cadastrar/', login_required(ProcedimentoPlasticaCreateView.as_view()), name='procedimento_plastica_create'),
    path('plastica/procedimento/lista/', login_required(ProcedimentoPlasticaListView.as_view()), name='procedimento_plastica_list'),
    path('plastica/procedimento/editar/<int:pk>/', login_required(ProcedimentoPlasticaUpdateView.as_view()), name='procedimento_plastica_update'),
    path('plastica/procedimento/excluir/<int:pk>/', login_required(ProcedimentoPlasticaDeleteView.as_view()), name='procedimento_plastica_delete'),

    # Atendimentos de Plástica
    path('plastica/atendimento/registrar/', login_required(RegistroAtendimentoPlasticaCreateView.as_view()), name='registro_atendimento_plastica_create'),
    path('plastica/atendimento/historico/', login_required(HistoricoAtendimentosPlasticaListView.as_view()), name='historico_atendimentos_plastica_list'),
    path('plastica/atendimento/editar/<int:pk>/', login_required(AtendimentoPlasticaUpdateView.as_view()), name='atendimento_plastica_update'),
    path('plastica/atendimento/excluir/<int:pk>/', login_required(AtendimentoPlasticaDeleteView.as_view()), name='atendimento_plastica_delete'),
    path('plastica/autocomplete/cliente/', login_required(ClienteAutocompletePlasticaView.as_view()), name='cliente_autocomplete_plastica'),

    
    # Pré-Agendamentos
    path('plastica/pre-agendamento/cadastrar/', login_required(PreAgendamentoPlasticaCreateView.as_view()), name='pre_agendamento_plastica_create'),
    path('plastica/pre-agendamento/lista/', login_required(PreAgendamentoPlasticaListView.as_view()), name='pre_agendamento_plastica_list'),
    path('plastica/pre-agendamento/editar/<int:pk>/', login_required(PreAgendamentoPlasticaUpdateView.as_view()), name='pre_agendamento_plastica_update'),
    path('plastica/pre-agendamento/excluir/<int:pk>/', login_required(PreAgendamentoPlasticaDeleteView.as_view()), name='pre_agendamento_plastica_delete'),
    path('plastica/pre-agendamento/status/<int:pk>/', login_required(PreAgendamentoPlasticaUpdateStatusView.as_view()), name='pre_agendamento_plastica_update_status'),
    path('plastica/agenda-pre-agendamento/', login_required(PreAgendamentoPlasticaCalendarView.as_view()), name='pre_agendamento_plastica_calendar'),
    path('plastica/agenda-pre-agendamento/update/', login_required(PreAgendamentoPlasticaUpdateEventView.as_view()), name='pre_agendamento_plastica_update_event'),
    
    # Contratos
    path('plastica/contrato/cadastrar/<int:cliente_id>/', login_required(ContratoPlasticaCreateView.as_view()), name='contrato_plastica_create'),
    path('plastica/contrato/lista/', login_required(ContratoPlasticaListView.as_view()), name='contrato_plastica_list'),
    path('plastica/contrato/editar/<int:pk>/', login_required(ContratoPlasticaUpdateView.as_view()), name='contrato_plastica_update'),
    path('plastica/contrato/excluir/<int:pk>/', login_required(ContratoPlasticaDeleteView.as_view()), name='contrato_plastica_delete'),
    path('plastica/contrato/pagamento/<int:pk>/', login_required(PagamentoContratoCreateView.as_view()), name='pagamento_contrato_create'),
    path('historico_pagamentos/<int:pk>/', login_required(HistoricoPagamentosView.as_view()), name='historico_pagamentos'),
    path('editar_pagamento/<int:pk>/', login_required(PagamentoUpdateView.as_view()), name='editar_pagamento'),
    
    path('relatorio-financeiro-plastica/', login_required(RelatorioFinanceiroPlasticaView.as_view()), name='relatorio_financeiro_plastica'),
    path('relatorio-financeiro-contrato/', login_required(RelatorioFinanceiroContratoView.as_view()), name='relatorio_financeiro_contrato'),
    path('plastica/exportar-excel/', ExportarAtendimentosPlasticaExcelView.as_view(), name='exportar_atendimentos_plastica'),
    path('plastica/exportar-contratos/', ExportarContratosPlasticaExcelView.as_view(), name='exportar_contratos_plastica'),

]   