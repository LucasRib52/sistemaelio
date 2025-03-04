from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView, View
from django.db import transaction
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
import json
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Case, When, IntegerField
import pandas as pd
from collections import defaultdict
import xlsxwriter
from django.db.models import Sum, F, Count, Exists, OuterRef
from django.utils.timezone import datetime
from datetime import timedelta
from .models import RegistroClientes
from django.db.models import Exists, OuterRef
import os
from django.conf import settings

from django.utils.dateparse import parse_datetime, parse_date
from .models import (
    RegistroAtendimentoPlastica,
    HistoricoProcedimentosPlastica,
    ProfissionalPlastica,
    ProcedimentosPlastica,
    PreAgendamentoPlastica,
    ContratoPlastica,
    PagamentoContrato
)
from .forms import (
    RegistroAtendimentoPlasticaForm,
    ProfissionalPlasticaForm,
    ProcedimentoPlasticaForm,
    PreAgendamentoPlasticaForm,
    PreAgendamentoPlasticaUpdateStatusForm,
    ContratoPlasticaForm,
    PagamentoContratoForm
)

# Profissional Views
class ProfissionalPlasticaCreateView(LoginRequiredMixin, CreateView):
    model = ProfissionalPlastica
    form_class = ProfissionalPlasticaForm
    template_name = 'profissionais/profissional_plastica_create.html'
    success_url = reverse_lazy('profissional_plastica_list')

class ProfissionalPlasticaListView(LoginRequiredMixin, ListView):
    model = ProfissionalPlastica
    template_name = 'profissionais/profissional_plastica_list.html'
    context_object_name = 'profissionais'
    paginate_by = 10

class ProfissionalPlasticaUpdateView(LoginRequiredMixin, UpdateView):
    model = ProfissionalPlastica
    form_class = ProfissionalPlasticaForm
    template_name = 'profissionais/profissional_plastica_form.html'
    success_url = reverse_lazy('profissional_plastica_list')

class ProfissionalPlasticaDeleteView(LoginRequiredMixin, DeleteView):
    model = ProfissionalPlastica
    template_name = 'profissionais/profissional_plastica_confirm_delete.html'
    success_url = reverse_lazy('profissional_plastica_list')

# Procedimento Views
class ProcedimentoPlasticaCreateView(LoginRequiredMixin, CreateView):
    model = ProcedimentosPlastica
    form_class = ProcedimentoPlasticaForm
    template_name = 'procedimentos/procedimento_plastica_create.html'
    success_url = reverse_lazy('procedimento_plastica_list')

class ProcedimentoPlasticaListView(LoginRequiredMixin, ListView):
    model = ProcedimentosPlastica
    template_name = 'procedimentos/procedimento_plastica_list.html'
    context_object_name = 'procedimentos'
    paginate_by = 10

class ProcedimentoPlasticaUpdateView(LoginRequiredMixin, UpdateView):
    model = ProcedimentosPlastica
    form_class = ProcedimentoPlasticaForm
    template_name = 'procedimentos/procedimento_plastica_update.html'
    success_url = reverse_lazy('procedimento_plastica_list')

class ProcedimentoPlasticaDeleteView(LoginRequiredMixin, DeleteView):
    model = ProcedimentosPlastica
    template_name = 'procedimentos/procedimento_plastica_confirm_delete.html'
    success_url = reverse_lazy('procedimento_plastica_list')

# Registro de Atendimento Views
class RegistroAtendimentoPlasticaCreateView(LoginRequiredMixin, CreateView):
    model = RegistroAtendimentoPlastica
    form_class = RegistroAtendimentoPlasticaForm
    template_name = 'atendimentos/registro_atendimento_plastica.html'
    success_url = reverse_lazy('historico_atendimentos_plastica_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        with transaction.atomic():
            # Criar histórico de atendimento
            HistoricoProcedimentosPlastica.objects.create(
                cliente=self.object.cliente,
                atendimento=self.object,
                profissional=self.object.profissional,
                preco=self.object.valor_pago,
                observacoes=self.object.descricao,
            )

            # ✅ Verifica se já existe qualquer contrato para este cliente
            contrato_existente = ContratoPlastica.objects.filter(cliente=self.object.cliente).exists()

            if not contrato_existente:
                ContratoPlastica.objects.create(
                    cliente=self.object.cliente,
                    celular=self.object.cliente.telefone,
                    procedimento="",
                    status=1  # Sem Contrato
                )

        return response

#historio de atendimentos
class HistoricoAtendimentosPlasticaListView(LoginRequiredMixin, ListView):
    model = HistoricoProcedimentosPlastica
    template_name = 'atendimentos/historico_atendimentos_plastica.html'
    context_object_name = 'atendimentos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente', 'atendimento')

        query = self.request.GET.get('q', '').strip()
        date_filter = self.request.GET.get('date_filter', '')
        filtro_status = self.request.GET.get('status', '')
        filtro_contrato = self.request.GET.get('contrato', '')
        order_by = self.request.GET.get('order_by', '')

        if query:
            queryset = queryset.filter(cliente__name__icontains=query)

        # 🔹 Tratamento do filtro de data
        if date_filter:
            date_range = date_filter.split(" to ")  
            if len(date_range) == 2:
                start_date = parse_date(date_range[0].strip())
                end_date = parse_date(date_range[1].strip())
                if start_date and end_date:
                    queryset = queryset.filter(atendimento__data__date__range=[start_date, end_date])

        # 🔹 Filtro por status de pagamento: "Pago" e "Cortesia"
        if filtro_status:
            if filtro_status == "pago":
                queryset = queryset.filter(preco__gt=0)
            elif filtro_status == "cortesia":
                queryset = queryset.filter(atendimento__forma_pagamento="Cortesia")

        # 🔹 Filtro por status do contrato
        contratos_existem = ContratoPlastica.objects.filter(cliente=OuterRef('cliente'))

        if filtro_contrato:
            if filtro_contrato == "com_contrato":
                queryset = queryset.annotate(tem_contrato=Exists(contratos_existem)).filter(tem_contrato=True)
            elif filtro_contrato == "sem_contrato":
                queryset = queryset.annotate(tem_contrato=Exists(contratos_existem)).filter(tem_contrato=False)
            elif filtro_contrato == "contrato_cancelado":
                queryset = queryset.filter(cliente__contratos_plastica__status=4)
            elif filtro_contrato == "contrato_finalizado":
                queryset = queryset.filter(cliente__contratos_plastica__status=3)

        # 🔹 Ordenação
        ordering_options = {
            "name_asc": "cliente__name",
            "name_desc": "-cliente__name",
            "date_asc": "atendimento__data",
            "date_desc": "-atendimento__data",
            "price_asc": "preco",
            "price_desc": "-preco"
        }

        if order_by in ordering_options:
            queryset = queryset.order_by(ordering_options[order_by])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['date_filter'] = self.request.GET.get('date_filter', '')
        context['status'] = self.request.GET.get('status', '')
        context['contrato'] = self.request.GET.get('contrato', '')
        context['order_by'] = self.request.GET.get('order_by', '')
        return context

class ClienteAutocompletePlasticaView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip()
        if term:
            # Filtra por nome ou telefone (pode incluir telefone secundário se desejar)
            clientes = RegistroClientes.objects.filter(
                Q(name__icontains=term) | Q(telefone__icontains=term)
            )[:10]
            cliente_list = [
                {
                    "id": cliente.id,
                    "label": cliente.name,
                    "telefone": cliente.telefone,
                    "telefone2": getattr(cliente, 'telefone2', '')
                }
                for cliente in clientes
            ]
            return JsonResponse(cliente_list, safe=False)
        return JsonResponse([], safe=False)

class AtendimentoPlasticaUpdateView(LoginRequiredMixin, UpdateView):
    model = HistoricoProcedimentosPlastica
    template_name = 'atendimentos/atendimento_update_plastica.html'
    form_class = RegistroAtendimentoPlasticaForm  
    success_url = reverse_lazy('historico_atendimentos_plastica_list')

    def form_valid(self, form):
        historico = form.save(commit=False)
        
        with transaction.atomic():
            atendimento = historico.atendimento
            atendimento.cliente = form.cleaned_data.get('cliente')
            atendimento.procedimento = form.cleaned_data.get('procedimento')
            atendimento.profissional = form.cleaned_data.get('profissional')
            atendimento.valor_pago = form.cleaned_data.get('valor_pago')
            atendimento.forma_pagamento = form.cleaned_data.get('forma_pagamento')
            atendimento.data = form.cleaned_data.get('data')
            atendimento.descricao = form.cleaned_data.get('descricao', '')

            # Se a forma de pagamento for "Cartão de Crédito", atualizar parcelas
            if atendimento.forma_pagamento == "Cartão de Crédito":
                atendimento.parcelas = int(form.cleaned_data.get('parcelas', 1))  # Conversão segura para inteiro
            else:
                atendimento.parcelas = 1  # Define como 1 caso não seja parcelado

            atendimento.save()

            historico.preco = atendimento.valor_pago
            historico.observacoes = atendimento.descricao
            historico.save()

        return super().form_valid(form)



class AtendimentoPlasticaDeleteView(LoginRequiredMixin, DeleteView):
    model = HistoricoProcedimentosPlastica
    template_name = 'atendimentos/atendimento_confirm_delete_plastica.html'
    success_url = reverse_lazy('historico_atendimentos_plastica_list')
    
    
# View para criar um pré-agendamento de Plástica
class PreAgendamentoPlasticaCreateView(LoginRequiredMixin, CreateView): 
    model = PreAgendamentoPlastica
    form_class = PreAgendamentoPlasticaForm
    template_name = 'pre_agendamento/pre_agendamento_plastica_create.html'
    success_url = reverse_lazy('pre_agendamento_plastica_list')

    def form_valid(self, form):
        pre_agendamento = form.save(commit=False)
        
        # Certificando-se de que 'procedimento' foi selecionado antes de salvar
        if not pre_agendamento.procedimento:
            form.add_error('procedimento', 'Selecione um procedimento válido.')
            return self.form_invalid(form)

        pre_agendamento.save()
        return super().form_valid(form)

# View para listar pré-agendamentos de Plástica
class PreAgendamentoPlasticaListView(LoginRequiredMixin, ListView):
    model = PreAgendamentoPlastica
    template_name = 'pre_agendamento/pre_agendamento_plastica_list.html'
    context_object_name = 'pre_agendamentos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cliente')
        query = self.request.GET.get('q', '').strip()
        date_filter = self.request.GET.get('date_filter', '')
        status = self.request.GET.get('status', '')

        if query:
            queryset = queryset.filter(nome__icontains=query)

        if date_filter:
            date_range = date_filter.split(" to ")
            if len(date_range) == 2:
                start_date = parse_date(date_range[0].strip())
                end_date = parse_date(date_range[1].strip())
                if start_date and end_date:
                    queryset = queryset.filter(data_agendamento__range=[start_date, end_date])

        if status:
            queryset = queryset.filter(posicao_agendamento=status)

        # Obter o mês atual (ex: se estiver em dezembro, current_month será 12)
        current_month = timezone.now().month

        # Anota os registros: prioridade 0 se data_consulta for do mês atual, ou 1 para os demais
        queryset = queryset.annotate(
            prioridade=Case(
                When(data_consulta__month=current_month, then=0),
                default=1,
                output_field=IntegerField()
            )
        )

        # Ordena primeiramente pela prioridade, depois pela data_consulta e pelo horário
        return queryset.order_by('prioridade', 'data_consulta', 'horario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['date_filter'] = self.request.GET.get('date_filter', '')
        context['status'] = self.request.GET.get('status', '')
        return context

# View para editar um pré-agendamento de Plástica
class PreAgendamentoPlasticaUpdateView(LoginRequiredMixin, UpdateView):
    model = PreAgendamentoPlastica
    form_class = PreAgendamentoPlasticaForm
    template_name = 'pre_agendamento/pre_agendamento_plastica_form.html'
    success_url = reverse_lazy('pre_agendamento_plastica_list')

# View para excluir um pré-agendamento de Plástica
class PreAgendamentoPlasticaDeleteView(LoginRequiredMixin, DeleteView):
    model = PreAgendamentoPlastica
    template_name = 'pre_agendamento/pre_agendamento_plastica_confirm_delete.html'
    success_url = reverse_lazy('pre_agendamento_plastica_list')

# View para atualizar o status do pré-agendamento de Plástica
class PreAgendamentoPlasticaUpdateStatusView(LoginRequiredMixin, UpdateView):
    model = PreAgendamentoPlastica
    form_class = PreAgendamentoPlasticaUpdateStatusForm
    template_name = 'pre_agendamento/pre_agendamento_plastica_update_status.html'
    success_url = reverse_lazy('pre_agendamento_plastica_list')

    def form_valid(self, form):
        pre_agendamento = form.save(commit=False)
        nova_data_consulta = self.request.POST.get('nova_data_consulta')
        novo_horario = self.request.POST.get('novo_horario')

        # Se o status for "Reagendado" (valor 2) e os campos de nova data/hora forem preenchidos
        if form.cleaned_data['posicao_agendamento'] == '2' and nova_data_consulta and novo_horario:
            pre_agendamento.data_consulta = nova_data_consulta
            pre_agendamento.horario = novo_horario

        # Se o status for "Confirmado" (valor 1) e o usuário indicar que já é cliente
        if form.cleaned_data['posicao_agendamento'] == '1' and form.cleaned_data.get('ja_e_cliente') == 'sim':
            from clientes.models import RegistroClientes
            # Exemplo: busca por cliente utilizando o número de celular
            cliente_existente = RegistroClientes.objects.filter(telefone=pre_agendamento.celular).first()
            if cliente_existente:
                pre_agendamento.cliente = cliente_existente

        pre_agendamento.save()
        return super().form_valid(form)

# View para exibir o calendário de pré-agendamentos de Plástica
class PreAgendamentoPlasticaCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'pre_agendamento/pre_agendamento_plastica_calendar.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            pre_agendamentos = PreAgendamentoPlastica.objects.all()
            eventos = [
                {
                    "id": pre_agendamento.id,
                    "title": pre_agendamento.nome,
                    "start": pre_agendamento.data_consulta.strftime('%Y-%m-%dT%H:%M:%S') if pre_agendamento.data_consulta else None,
                    "extendedProps": {
                        "celular": pre_agendamento.celular,
                        "data_consulta": pre_agendamento.data_consulta.strftime('%d/%m/%Y') if pre_agendamento.data_consulta else "Não informada",
                        "horario": pre_agendamento.horario.strftime('%H:%M') if pre_agendamento.horario else "Não informado",
                        "procedimento": pre_agendamento.procedimento,
                        "posicao_agendamento": pre_agendamento.get_posicao_agendamento_display(),
                        "observacoes": pre_agendamento.observacoes or "Nenhuma observação",
                    },
                    "classNames": self.get_event_class(pre_agendamento.posicao_agendamento)
                }
                for pre_agendamento in pre_agendamentos
            ]
            return JsonResponse(eventos, safe=False)
        return super().get(request, *args, **kwargs)

    def get_event_class(self, status):
        status_classes = {
            1: 'confirmado',
            2: 'reagendado',
            3: 'desmarcado',
            4: 'sem-resposta',
        }
        return status_classes.get(status, 'sem-resposta')

# View para atualizar eventos de pré-agendamento de Plástica
class PreAgendamentoPlasticaUpdateEventView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            pre_agendamento = get_object_or_404(PreAgendamentoPlastica, id=data['id'])

            action = data.get('action')

            if action == 'confirmado':
                pre_agendamento.posicao_agendamento = 1
            elif action == 'reagendado':
                new_date_str = data.get('start')
                if new_date_str:
                    new_date = parse_datetime(new_date_str).date()
                    pre_agendamento.data_consulta = new_date
                    pre_agendamento.posicao_agendamento = 2
            elif action == 'desmarcado':
                pre_agendamento.posicao_agendamento = 3

            pre_agendamento.save()
            return JsonResponse({
                "success": True,
                "message": "Status atualizado com sucesso.",
                "new_date": pre_agendamento.data_consulta.strftime('%Y-%m-%d'),
                "posicao_agendamento": pre_agendamento.get_posicao_agendamento_display()
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        


# Criar contrato
class ContratoPlasticaCreateView(LoginRequiredMixin, CreateView):
    model = ContratoPlastica
    form_class = ContratoPlasticaForm
    template_name = 'contratos/contrato_form.html'
    success_url = reverse_lazy('contrato_plastica_list')

    def get_initial(self):
        initial = super().get_initial()
        cliente_id = self.kwargs.get('cliente_id')

        if cliente_id:
            initial['cliente'] = cliente_id

        return initial
    
# Listar contratos
class ContratoPlasticaListView(LoginRequiredMixin, ListView):
    model = ContratoPlastica
    template_name = 'contratos/contrato_list.html'
    context_object_name = 'contratos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '')
        status = self.request.GET.get('status', '')
        data_contrato_range = self.request.GET.get('data_contrato_range', '')
        data_validade_range = self.request.GET.get('data_validade_range', '')

        if q:
            queryset = queryset.filter(Q(cliente__nome__icontains=q) | Q(celular__icontains=q))
        if status:
            queryset = queryset.filter(status=status)
        if data_contrato_range:
            dates = data_contrato_range.split(" to ")
            if len(dates) == 2:
                queryset = queryset.filter(data_contrato__range=[parse_date(dates[0]), parse_date(dates[1])])
        if data_validade_range:
            dates = data_validade_range.split(" to ")
            if len(dates) == 2:
                queryset = queryset.filter(data_validade__range=[parse_date(dates[0]), parse_date(dates[1])])

        return queryset


# Atualizar contrato
class ContratoPlasticaUpdateView(LoginRequiredMixin, UpdateView):
    model = ContratoPlastica
    form_class = ContratoPlasticaForm
    template_name = 'contratos/contrato_form.html'
    success_url = reverse_lazy('contrato_plastica_list')

    def form_valid(self, form):
        contrato = form.save(commit=False)

        # ✅ Se o contrato for editado e o status for alterado, salva a mudança
        if contrato.status == 1:  # Se estava como "Sem Contrato"
            contrato.status = 2  # Agora passa para "Com Contrato"
        
        contrato.save()
        return super().form_valid(form)
    
# Deletar contrato
class ContratoPlasticaDeleteView(LoginRequiredMixin, DeleteView):
    model = ContratoPlastica
    template_name = 'contratos/contrato_confirm_delete.html'
    success_url = reverse_lazy('contrato_plastica_list')
    
    
class PagamentoContratoCreateView(LoginRequiredMixin, CreateView):
    model = PagamentoContrato
    form_class = PagamentoContratoForm
    template_name = 'contratos/pagamento_form.html'

    def get_success_url(self):
        return reverse_lazy('contrato_plastica_list')

    def form_valid(self, form):
        contrato = get_object_or_404(ContratoPlastica, pk=self.kwargs['pk'])
        pagamento = form.save(commit=False)
        pagamento.contrato = contrato

        # ✅ Salva o comprovante corretamente na pasta media/comprovantes/
        if 'comprovante' in self.request.FILES:
            comprovante = self.request.FILES['comprovante']
            comprovante_path = os.path.join(settings.MEDIA_ROOT, 'comprovantes', comprovante.name)

            # Verifica se o diretório existe, se não, cria
            os.makedirs(os.path.dirname(comprovante_path), exist_ok=True)

            # Salva o arquivo no diretório correto
            with open(comprovante_path, 'wb+') as destination:
                for chunk in comprovante.chunks():
                    destination.write(chunk)

            pagamento.comprovante = f"comprovantes/{comprovante.name}"

        pagamento.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """ Adiciona o contrato ao contexto para exibir os valores corretamente """
        context = super().get_context_data(**kwargs)
        context['contrato'] = get_object_or_404(ContratoPlastica, pk=self.kwargs['pk'])
        return context

    
class HistoricoPagamentosView(LoginRequiredMixin, View):
    template_name = "contratos/historico_pagamentos.html"

    def get(self, request, pk):
        contrato = get_object_or_404(ContratoPlastica, pk=pk)
        pagamentos = contrato.pagamentos.all().order_by("-data_pagamento")  # ✅ Ordenação do mais recente para o mais antigo
        return render(request, self.template_name, {'contrato': contrato, 'pagamentos': pagamentos})
    
class PagamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = PagamentoContrato
    form_class = PagamentoContratoForm
    template_name = "contratos/editar_pagamento.html"

    def get_success_url(self):
        return reverse_lazy('historico_pagamentos', kwargs={'pk': self.object.contrato.pk})

    def form_valid(self, form):
        pagamento = form.save(commit=False)

        # ✅ Garante que a data do pagamento seja mantida corretamente na edição
        if not pagamento.data_pagamento:
            pagamento.data_pagamento = form.cleaned_data.get("data_pagamento")

        pagamento.save()
        return super().form_valid(form)
    
    
    
class RelatorioFinanceiroPlasticaView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorio_financeiro_plastica.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtendo anos e meses disponíveis
        anos = RegistroAtendimentoPlastica.objects.dates('data', 'year', order="DESC")
        meses = [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'), (5, 'Maio'),
            (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'), (10, 'Outubro'),
            (11, 'Novembro'), (12, 'Dezembro')
        ]

        # Obtendo ano e mês da URL ou valores padrão
        ano_selecionado = self.request.GET.get('ano', datetime.now().year)
        mes_selecionado = self.request.GET.get('mes')

        try:
            ano_selecionado = int(ano_selecionado)
            mes_selecionado = int(mes_selecionado) if mes_selecionado else None
        except ValueError:
            ano_selecionado = datetime.now().year
            mes_selecionado = None

        # 🔹 Filtrar apenas os atendimentos que existem no histórico e não foram excluídos
        queryset = HistoricoProcedimentosPlastica.objects.filter(
            atendimento__data__year=ano_selecionado
        )

        if mes_selecionado:
            queryset = queryset.filter(atendimento__data__month=mes_selecionado)

        # 🔹 Total de consultas realizadas no mês selecionado
        total_consultas = queryset.count()

        # 🔹 Criar um conjunto para armazenar clientes únicos com contrato
        clientes_com_contrato = set()

        # 🔹 Criar dicionário para total de contratos e consultas por mês
        total_contratos_por_mes = defaultdict(int)
        total_consultas_por_mes = defaultdict(int)

        for registro in queryset:
            total_consultas_por_mes[registro.atendimento.data.month] += 1

            # ✅ Contar um cliente apenas uma vez se ele tiver um contrato ativo
            if ContratoPlastica.objects.filter(cliente=registro.cliente, status=2).exists():
                if registro.cliente.id not in clientes_com_contrato:
                    clientes_com_contrato.add(registro.cliente.id)
                    total_contratos_por_mes[registro.atendimento.data.month] += 1

        # 🔹 Selecione apenas contratos existentes no mês filtrado
        total_com_contrato = (
            total_contratos_por_mes[mes_selecionado] if mes_selecionado else len(clientes_com_contrato)
        )

        # 🔹 Controle de valores parcelados
        valores_parcelados = defaultdict(float)
        total_parcelado_geral = 0.0

        for atendimento in RegistroAtendimentoPlastica.objects.filter(
            data__year=ano_selecionado, 
            parcelas__gt=1
    ).filter(
        Exists(HistoricoProcedimentosPlastica.objects.filter(atendimento=OuterRef('pk')))
    ):
            parcela_valor = float(atendimento.valor_pago / atendimento.parcelas)
            data_parcela = atendimento.data.date()

            for i in range(atendimento.parcelas):
                data_mensal = data_parcela + timedelta(days=30 * i)
                if data_mensal.year == ano_selecionado:
                    valores_parcelados[data_mensal.month] += parcela_valor

            total_parcelado_geral += float(atendimento.valor_pago)

        # 🔹 Se um mês foi filtrado, mostrar apenas os valores desse mês nos gráficos
        if mes_selecionado:
            valores_parcelados = {mes_selecionado: valores_parcelados.get(mes_selecionado, 0)}

        valores_parcelados_json = json.dumps({int(k): v for k, v in valores_parcelados.items()})
        valor_parcelado_filtro = valores_parcelados.get(mes_selecionado, 0) if mes_selecionado else total_parcelado_geral

        # 🔹 Filtrando arrecadação corretamente para o mês selecionado
        total_arrecadado = float(queryset.aggregate(total=Sum('atendimento__valor_pago'))['total'] or 0)

        # 🔹 Criando dados para gráficos
        total_arrecadado_por_mes = defaultdict(float)

        for registro in queryset:
            total_arrecadado_por_mes[registro.atendimento.data.month] += float(registro.atendimento.valor_pago)

        # 🔹 Removendo meses sem dados para evitar gráficos subindo sem motivo
        if mes_selecionado:
            total_arrecadado_por_mes = {mes_selecionado: total_arrecadado_por_mes.get(mes_selecionado, 0)}
            total_contratos_por_mes = {mes_selecionado: total_contratos_por_mes.get(mes_selecionado, 0)}
            total_consultas_por_mes = {mes_selecionado: total_consultas_por_mes.get(mes_selecionado, 0)}

        arrecadado_json = json.dumps({int(k): v for k, v in total_arrecadado_por_mes.items()})
        consultas_json = json.dumps({int(k): v for k, v in total_consultas_por_mes.items()})
        contratos_json = json.dumps({int(k): v for k, v in total_contratos_por_mes.items()})

        # ✅ Adicionando os dados no contexto
        context.update({
            'total_consultas': total_consultas,
            'total_com_contrato': total_com_contrato,
            'total_arrecadado': total_arrecadado,
            'valor_parcelado_filtro': valor_parcelado_filtro,
            'anos': [a.year for a in anos],
            'meses': meses,
            'ano_selecionado': ano_selecionado,
            'mes_selecionado': mes_selecionado,
            'valores_parcelados_json': valores_parcelados_json,
            'arrecadado_json': arrecadado_json,
            'consultas_json': consultas_json,
            'contratos_json': contratos_json,
        })

        return context
    

class RelatorioFinanceiroContratoView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorio_financeiro_contrato.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtendo anos e meses disponíveis
        anos = ContratoPlastica.objects.dates('data_contrato', 'year', order="DESC")
        meses = [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'), (5, 'Maio'),
            (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'), (10, 'Outubro'),
            (11, 'Novembro'), (12, 'Dezembro')
        ]

        # Obtendo ano e mês da URL ou valores padrão
        ano_selecionado = self.request.GET.get('ano', datetime.now().year)
        mes_selecionado = self.request.GET.get('mes')

        try:
            ano_selecionado = int(ano_selecionado)
            mes_selecionado = int(mes_selecionado) if mes_selecionado else None
        except ValueError:
            ano_selecionado = datetime.now().year
            mes_selecionado = None

        # 🔹 Filtrar contratos no ano/mês selecionado
        queryset = ContratoPlastica.objects.filter(data_contrato__year=ano_selecionado)

        if mes_selecionado:
            queryset = queryset.filter(data_contrato__month=mes_selecionado)

        # 🔹 Totais
        total_contratos = queryset.count()
        total_contrato_finalizado = queryset.filter(status=3).count()  # Status 3 = Finalizado
        total_com_contrato = queryset.filter(status=2).count()  # Status 2 = Em andamento

        valor_total = float(queryset.aggregate(Sum('valor_total'))['valor_total__sum'] or 0)
        valor_pago = float(sum(float(contrato.total_pago()) for contrato in queryset))
        valor_faltante = valor_total - valor_pago

        # 🔹 Criando dados para gráficos
        total_contratos_por_mes = defaultdict(int)
        contratos_finalizados_por_mes = defaultdict(int)
        valores_totais_por_mes = defaultdict(float)
        valores_faltantes_por_mes = defaultdict(float)
        valores_pagos_por_mes = defaultdict(float)

        for contrato in queryset:
            mes = contrato.data_contrato.month
            total_contratos_por_mes[mes] += 1
            valores_totais_por_mes[mes] += float(contrato.valor_total or 0)
            valores_faltantes_por_mes[mes] += float(contrato.valor_faltante())
            valores_pagos_por_mes[mes] += float(contrato.total_pago())

            if contrato.status == 3:  # Se for finalizado
                contratos_finalizados_por_mes[mes] += 1

        # 🔹 Se um mês foi filtrado, mostrar apenas os valores desse mês nos gráficos
        if mes_selecionado:
            total_contratos_por_mes = {mes_selecionado: total_contratos_por_mes.get(mes_selecionado, 0)}
            contratos_finalizados_por_mes = {mes_selecionado: contratos_finalizados_por_mes.get(mes_selecionado, 0)}
            valores_totais_por_mes = {mes_selecionado: valores_totais_por_mes.get(mes_selecionado, 0)}
            valores_faltantes_por_mes = {mes_selecionado: valores_faltantes_por_mes.get(mes_selecionado, 0)}
            valores_pagos_por_mes = {mes_selecionado: valores_pagos_por_mes.get(mes_selecionado, 0)}

        # 🔹 Convertendo para JSON
        contratos_json = json.dumps({int(k): v for k, v in total_contratos_por_mes.items()})
        contratos_finalizados_json = json.dumps({int(k): v for k, v in contratos_finalizados_por_mes.items()})
        valores_totais_json = json.dumps({int(k): v for k, v in valores_totais_por_mes.items()})
        valores_faltantes_json = json.dumps({int(k): v for k, v in valores_faltantes_por_mes.items()})
        valores_pagos_json = json.dumps({int(k): v for k, v in valores_pagos_por_mes.items()})

        # ✅ Adicionando os dados no contexto
        context.update({
            'total_contratos': total_contratos,
            'total_contrato_finalizado': total_contrato_finalizado,
            'total_com_contrato': total_com_contrato,
            'valor_total': valor_total,
            'valor_pago': valor_pago,
            'valor_faltante': valor_faltante,
            'anos': [a for a in anos],
            'meses': meses,
            'ano_selecionado': ano_selecionado,
            'mes_selecionado': mes_selecionado,
            'contratos_json': contratos_json,
            'contratos_finalizados_json': contratos_finalizados_json,
            'valores_totais_json': valores_totais_json,
            'valores_faltantes_json': valores_faltantes_json,
            'valores_pagos_json': valores_pagos_json,
        })

        return context
    
    
class ExportarAtendimentosPlasticaExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        atendimentos = RegistroAtendimentoPlastica.objects.select_related('cliente')
        
        # Criando a lista de dados
        dados = []
        for atendimento in atendimentos:
            # Determinar status do contrato
            if hasattr(atendimento.cliente, 'contratos_plastica') and atendimento.cliente.contratos_plastica.exists():
                contrato = atendimento.cliente.contratos_plastica.first()
                status_contrato = contrato.get_status_display()
            else:
                status_contrato = "Sem Contrato"
                
            dados.append({
                "Nome do Paciente": atendimento.cliente.name if atendimento.cliente else "N/A",
                "Procedimento": atendimento.procedimento,
                "Data": atendimento.data.strftime('%d/%m/%Y %H:%M'),
                "Valor Pago": float(atendimento.valor_pago),
                "Forma de Pagamento": atendimento.forma_pagamento,
                "Parcelas": atendimento.parcelas if atendimento.parcelas else "-",
                "Status de Pagamento": "Pago" if atendimento.valor_pago > 0 else "Pendente",
                "Status do Contrato": status_contrato,
            })
        
        # Criando DataFrame
        df = pd.DataFrame(dados)
        
        # Criando resposta HTTP com o tipo de arquivo correto
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=atendimentos_plastica.xlsx'
        
        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Atendimentos Plástica', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Atendimentos Plástica']
            
            # Formatando o cabeçalho
            header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#007bff', 'font_color': 'white', 'border': 1})
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Ajustando colunas automaticamente
            for col_num, col_name in enumerate(df.columns):
                max_length = max(df[col_name].astype(str).map(len).max(), len(col_name)) + 2
                worksheet.set_column(col_num, col_num, max_length)
        
        return response
    
    
class ExportarContratosPlasticaExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        contratos = ContratoPlastica.objects.prefetch_related('pagamentos')
        
        # Definir o número máximo de pagamentos a serem exibidos
        max_pagamentos = max(contrato.pagamentos.count() for contrato in contratos) if contratos else 0
        
        # Criando a lista de dados
        dados = []
        for contrato in contratos:
            pagamentos = contrato.pagamentos.all()
            pagamento_dados = []
            
            for pagamento in pagamentos:
                pagamento_dados.append(f"R$ {pagamento.valor} - {pagamento.data_pagamento.strftime('%d/%m/%Y')}")
            
            linha_dados = {
                "Cliente": contrato.cliente.name,
                "Celular": contrato.celular,
                "Valor Total": float(contrato.valor_total) if contrato.valor_total else 0.00,
                "Valor Pago": float(contrato.total_pago()),
                "Valor Faltante": float(contrato.valor_faltante()),
                "Data do Contrato": contrato.data_contrato.strftime('%d/%m/%Y') if contrato.data_contrato else "-",
                "Data de Validade": contrato.data_validade.strftime('%d/%m/%Y') if contrato.data_validade else "-",
                "Status": contrato.get_status_display(),
            }
            
            # Adicionando colunas dinâmicas para pagamentos
            for i in range(max_pagamentos):
                linha_dados[f"Pagamento {i+1}"] = pagamento_dados[i] if i < len(pagamento_dados) else "-"
            
            dados.append(linha_dados)
        
        # Criando DataFrame
        df = pd.DataFrame(dados)
        
        # Criando resposta HTTP com o tipo de arquivo correto
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=contratos_plastica.xlsx'
        
        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Contratos Plástica', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Contratos Plástica']
            
            # Formatando o cabeçalho
            header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#007bff', 'font_color': 'white', 'border': 1})
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Ajustando colunas automaticamente
            for col_num, col_name in enumerate(df.columns):
                max_length = max(df[col_name].astype(str).map(len).max(), len(col_name)) + 2
                worksheet.set_column(col_num, col_num, max_length)
        
        return response
