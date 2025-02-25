from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    ProfissionalCreateView,
    ProfissionalListView,
    ProfissionalUpdateView,
    ProfissionalDeleteView,
    ProcedimentoCreateView,
    ProcedimentoListView,
    ProcedimentoUpdateView,
    ProcedimentoDeleteView,
    RegistroAtendimentoCreateView,
    HistoricoAtendimentosListView,
    AtendimentoUpdateView,
    AtendimentoDeleteView,
    AtendimentoUpdatePaymentView,
    ClienteAutocompleteView,
    ClienteAutocompletePhoneView,
    PreAgendamentoCreateView,
    PreAgendamentoListView,
    PreAgendamentoUpdateView,
    PreAgendamentoDeleteView,
    PreAgendamentoUpdateStatusView,
    PreAgendamentoCalendarView,
    PreAgendamentoUpdateEventView,
    ProcedimentoAutocompleteView,
    RelatorioFinanceiroView,
    ExportarHistoricoExcelView,
)

urlpatterns = [
    # Profissionais
    path('profissional/cadastrar/', login_required(ProfissionalCreateView.as_view()), name='profissional_create'),
    path('profissional/lista/', login_required(ProfissionalListView.as_view()), name='profissional_list'),
    path('profissional/editar/<int:pk>/', login_required(ProfissionalUpdateView.as_view()), name='profissional_update'),
    path('profissional/excluir/<int:pk>/', login_required(ProfissionalDeleteView.as_view()), name='profissional_delete'),

    # Procedimentos
    path('procedimento/cadastrar/', login_required(ProcedimentoCreateView.as_view()), name='procedimento_create'),
    path('procedimento/lista/', login_required(ProcedimentoListView.as_view()), name='procedimento_list'),
    path('procedimento/editar/<int:pk>/', login_required(ProcedimentoUpdateView.as_view()), name='procedimento_update'),
    path('procedimento/excluir/<int:pk>/', login_required(ProcedimentoDeleteView.as_view()), name='procedimento_delete'),
    path('procedimentos/autocomplete/', login_required(ProcedimentoAutocompleteView.as_view()), name='procedimento_autocomplete'),

    # Atendimentos
    path('atendimento/registrar/', login_required(RegistroAtendimentoCreateView.as_view()), name='registro_atendimento_create'),
    path('atendimento/historico/', login_required(HistoricoAtendimentosListView.as_view()), name='historico_atendimentos_list'),
    path('atendimento/editar/<int:pk>/', login_required(AtendimentoUpdateView.as_view()), name='atendimento_update'),
    path('atendimento/excluir/<int:pk>/', login_required(AtendimentoDeleteView.as_view()), name='atendimento_delete'),
    path('atendimento/atualizar-pagamento/<int:pk>/', login_required(AtendimentoUpdatePaymentView.as_view()), name='atendimento_update_payment'),
    path('autocomplete/cliente/', login_required(ClienteAutocompleteView.as_view()), name='cliente_autocomplete'),
    path('autocomplete/cliente-telefone/', ClienteAutocompletePhoneView.as_view(), name='cliente_autocomplete_phone'),

    
    # Pré-Agendamentos
    path('pre-agendamento/cadastrar/', login_required(PreAgendamentoCreateView.as_view()), name='pre_agendamento_create'),
    path('pre-agendamento/lista/', login_required(PreAgendamentoListView.as_view()), name='pre_agendamento_list'),
    path('pre-agendamento/editar/<int:pk>/', login_required(PreAgendamentoUpdateView.as_view()), name='pre_agendamento_update'),
    path('pre-agendamento/excluir/<int:pk>/', login_required(PreAgendamentoDeleteView.as_view()), name='pre_agendamento_delete'),
    path('pre-agendamento/status/<int:pk>/', login_required(PreAgendamentoUpdateStatusView.as_view()), name='pre_agendamento_update_status'),
    path('agenda-pre-agendamento/', login_required(PreAgendamentoCalendarView.as_view()), name='pre_agendamento_calendar'),
    path('agenda-pre-agendamento/update/', login_required(PreAgendamentoUpdateEventView.as_view()), name='pre_agendamento_update_event'),

    path('relatorio-financeiro/', login_required(RelatorioFinanceiroView.as_view()), name='relatorio_financeiro'),
    path('atendimento/exportar-excel/', login_required(ExportarHistoricoExcelView.as_view()), name='exportar_historico_excel'),

]