from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView, View
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.db import transaction
import pandas as pd
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
import json
import xlsxwriter
from collections import defaultdict
from django.db.models import Exists, OuterRef, F, Sum  # ✅ Import necessário para evitar o erro
from django.utils.dateparse import parse_datetime
from .models import (
    RegistroAtendimento,
    HistoricoProcedimentos,
    Profissional,
    Procedimentos,
    RegistroClientes, 
    PreAgendamento
)
from .forms import (
    RegistroAtendimentoForm,
    ProfissionalForm,
    ProcedimentoForm,
    PreAgendamentoForm,
    PreAgendamentoUpdateStatusForm,
)

# View para cadastrar um profissional
class ProfissionalCreateView(LoginRequiredMixin, CreateView):
    model = Profissional  # Define o modelo para cadastro
    form_class = ProfissionalForm  # Usa o formulário correspondente
    template_name = 'profissionais/profissional_create.html'  # Template para renderização
    success_url = reverse_lazy('profissional_list')  # Redireciona após sucesso

# View para listar profissionais
class ProfissionalListView(LoginRequiredMixin, ListView):
    model = Profissional  # Define o modelo para listagem
    template_name = 'profissionais/profissional_list.html'  # Template para renderização
    context_object_name = 'profissionais'  # Nome do contexto para uso no template
    paginate_by = 10  # Limita o número de itens por página
    
    # Atualização de profissional
class ProfissionalUpdateView(LoginRequiredMixin, UpdateView):
    model = Profissional
    form_class = ProfissionalForm
    template_name = 'profissionais/profissional_form.html'
    success_url = reverse_lazy('profissional_list')
    
    # Exclusão de profissional
class ProfissionalDeleteView(LoginRequiredMixin, DeleteView):
    model = Profissional
    template_name = 'profissionais/profissional_confirm_delete.html'
    success_url = reverse_lazy('profissional_list')

# View para cadastrar um procedimento
class ProcedimentoCreateView(LoginRequiredMixin, CreateView):
    model = Procedimentos  # Define o modelo para cadastro
    form_class = ProcedimentoForm  # Usa o formulário correspondente
    template_name = 'procedimentos/procedimento_create.html'  # Template para renderização
    success_url = reverse_lazy('procedimento_list')  # Redireciona após sucesso

# View para listar procedimentos
class ProcedimentoListView(LoginRequiredMixin, ListView):
    model = Procedimentos  # Define o modelo para listagem
    template_name = 'procedimentos/procedimento_list.html'  # Template para renderização
    context_object_name = 'procedimentos'  # Nome do contexto para uso no template
    paginate_by = 10  # Limita o número de itens por página
    
    # View para editar um procedimento
class ProcedimentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Procedimentos  # Define o modelo para edição
    form_class = ProcedimentoForm  # Usa o formulário correspondente
    template_name = 'procedimentos/procedimento_form.html'  # Template para renderização
    success_url = reverse_lazy('procedimento_list')  # Redireciona após sucesso

# View para excluir um procedimento
class ProcedimentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Procedimentos  # Define o modelo para exclusão
    template_name = 'procedimentos/procedimento_confirm_delete.html'  # Template para renderização
    success_url = reverse_lazy('procedimento_list')  # Redireciona após sucesso


class ClienteAutocompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip()
        if term:
            # Buscar clientes cujo nome contém o termo digitado
            clientes = RegistroClientes.objects.filter(name__icontains=term)[:10]
            cliente_list = [
                {
                    "id": cliente.id,
                    "text": f"{cliente.name} - {cliente.telefone}",  # Nome e telefone para exibição
                    "label": cliente.name,  # Apenas o nome
                    "telefone": cliente.telefone,  # Telefone principal
                }
                for cliente in clientes
            ]
            return JsonResponse(cliente_list, safe=False)
        return JsonResponse([], safe=False)
    
class ClienteAutocompletePhoneView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip()
        if term:
            # Filtra APENAS por telefone (e telefone2 se existir)
            clientes = RegistroClientes.objects.filter(
                Q(telefone__icontains=term) |
                Q(telefone2__icontains=term)
            )[:10]
            cliente_list = []
            for cliente in clientes:
                cliente_list.append({
                    "id": cliente.id,
                    "label": cliente.telefone,  # o que aparece no dropdown
                    "name": cliente.name,       # nome completo para preencher outro campo
                    "telefone": cliente.telefone,
                    "telefone2": getattr(cliente, 'telefone2', '')
                })
            return JsonResponse(cliente_list, safe=False)
        return JsonResponse([], safe=False)

class ProcedimentoAutocompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '').strip()
        if term:
            # Buscar procedimentos cujo nome contém o termo digitado
            procedimentos = Procedimentos.objects.filter(nome__icontains=term)[:10]
            procedimento_list = [
                {
                    "id": procedimento.id,
                    "text": f"{procedimento.nome} - R$ {procedimento.preco_base}",  # Alterado para preco_base
                    "label": procedimento.nome,
                    "preco": str(procedimento.preco_base),  # Alterado para preco_base
                }
                for procedimento in procedimentos
            ]
            return JsonResponse(procedimento_list, safe=False)
        return JsonResponse([], safe=False)
    
class RegistroAtendimentoCreateView(LoginRequiredMixin, CreateView):
    model = RegistroAtendimento
    form_class = RegistroAtendimentoForm
    template_name = 'atendimentos/registro_atendimento_create.html'
    success_url = reverse_lazy('historico_atendimentos_list')

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save(commit=False)  
            self.object.quantidade_sessoes = form.cleaned_data['quantidade_sessoes']
            self.object.save()

            print(f"🟢 Salvando atendimento: Cliente={self.object.cliente}, Sessões={self.object.quantidade_sessoes}")

            # Criar entrada no histórico de procedimentos
            historico = HistoricoProcedimentos.objects.create(
                cliente=self.object.cliente,
                procedimento=self.object.procedimento,
                atendimento=self.object,
                profissional=self.object.profissional,
                preco=self.object.valor_total,
                quantidade_sessoes=self.object.quantidade_sessoes,  # 🆕 Pegando direto do atendimento
                observacoes=self.object.descricao,
            )

            print(f"🔵 Histórico salvo: Cliente={historico.cliente}, Sessões={historico.quantidade_sessoes}")

        return super().form_valid(form)


# View para listar o histórico de atendimentos
class HistoricoAtendimentosListView(LoginRequiredMixin, ListView):
    model = HistoricoProcedimentos
    template_name = 'atendimentos/historico_atendimentos_list.html'
    context_object_name = 'atendimentos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'cliente', 'procedimento', 'atendimento', 'profissional'
        )

        query = self.request.GET.get('q')
        filtro_procedimento = self.request.GET.get('procedimento')
        filtro_profissional = self.request.GET.get('profissional')
        filtro_status = self.request.GET.get('status')
        filtro_data = self.request.GET.get('data')

        if query:
            queryset = queryset.filter(cliente__name__icontains=query)

        if filtro_procedimento:
            queryset = queryset.filter(procedimento_id=filtro_procedimento)

        if filtro_profissional:
            queryset = queryset.filter(profissional_id=filtro_profissional)

        if filtro_data:
            data_formatada = parse_date(filtro_data)
            if data_formatada:
                queryset = queryset.filter(atendimento__data__date=data_formatada)

        if filtro_status:
            if filtro_status == "pago":
                queryset = queryset.filter(atendimento__valor_pago__gte=F("atendimento__valor_total"))
            elif filtro_status == "pendente":
                queryset = queryset.filter(atendimento__valor_pago__lt=F("atendimento__valor_total"))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['procedimentos'] = Procedimentos.objects.all()
        context['profissionais'] = Profissional.objects.all()
        return context

# View para editar informações de um atendimento
class AtendimentoUpdateView(LoginRequiredMixin, UpdateView):
    model = HistoricoProcedimentos  # Define o modelo para edição
    template_name = 'atendimentos/atendimentos_update.html'  # Template para renderização
    fields = ['cliente', 'procedimento', 'profissional', 'observacoes']  # Campos editáveis
    success_url = reverse_lazy('historico_atendimentos_list')  # Redireciona após sucesso

# View para deletar um atendimento
class AtendimentoDeleteView(LoginRequiredMixin, DeleteView):
    model = HistoricoProcedimentos
    template_name = 'atendimentos/atendimentos_delete.html'
    success_url = reverse_lazy('historico_atendimentos_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        with transaction.atomic():
            # 🟢 Deleta primeiro o RegistroAtendimento antes do histórico
            if self.object.atendimento:
                self.object.atendimento.delete()
            
            # 🔴 Agora deleta o histórico de procedimentos
            self.object.delete()

        return JsonResponse({'success': True, 'message': 'Atendimento deletado com sucesso!'})

# View para atualizar pagamentos pendentes
class AtendimentoUpdatePaymentView(LoginRequiredMixin, UpdateView):
    model = RegistroAtendimento
    template_name = 'atendimentos/atendimentos_update_payment.html'
    fields = []
    success_url = reverse_lazy('historico_atendimentos_list')

    def post(self, request, *args, **kwargs):
        atendimento = self.get_object()
        novo_valor = request.POST.get('valor_pago', 0)

        try:
            novo_valor = Decimal(novo_valor)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Valor inválido."}, status=400)

        # Valida se o novo valor excede o valor faltante
        if novo_valor > atendimento.valor_total - atendimento.valor_pago:
            return JsonResponse({"error": "O valor pago não pode exceder o valor faltante."}, status=400)

        atendimento.valor_pago += novo_valor
        if atendimento.valor_pago >= atendimento.valor_total:
            atendimento.valor_pago = atendimento.valor_total  # Limita ao valor total

        atendimento.save()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        historico = HistoricoProcedimentos.objects.get(atendimento=self.object)
        valor_faltante = historico.atendimento.valor_total - historico.atendimento.valor_pago
        context['atendimento'] = historico
        context['valor_faltante'] = valor_faltante
        return context
    
    
# Pre agendamento
class PreAgendamentoCreateView(LoginRequiredMixin, CreateView):
    model = PreAgendamento
    form_class = PreAgendamentoForm
    template_name = 'pre_agendamento/pre_agendamento_create.html'
    success_url = reverse_lazy('pre_agendamento_list')

    def form_valid(self, form):
        pre_agendamento = form.save(commit=False)
        
        # Certificando-se de que 'procedimento' foi selecionado antes de salvar
        if not pre_agendamento.procedimento:
            form.add_error('procedimento', 'Selecione um procedimento válido.')
            return self.form_invalid(form)
        
        pre_agendamento.save()
        return super().form_valid(form)

# View para listar pré-agendamentos
class PreAgendamentoListView(LoginRequiredMixin, ListView):
    model = PreAgendamento
    template_name = 'pre_agendamento/pre_agendamento_list.html'
    context_object_name = 'pre_agendamentos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
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

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['date_filter'] = self.request.GET.get('date_filter', '')
        context['status'] = self.request.GET.get('status', '')
        return context


# View para editar um pré-agendamento (sem o campo de status)
class PreAgendamentoUpdateView(LoginRequiredMixin, UpdateView):
    model = PreAgendamento
    form_class = PreAgendamentoForm
    template_name = 'pre_agendamento/pre_agendamento_form.html'
    success_url = reverse_lazy('pre_agendamento_list')

# View para excluir um pré-agendamento
class PreAgendamentoDeleteView(LoginRequiredMixin, DeleteView):
    model = PreAgendamento
    template_name = 'pre_agendamento/pre_agendamento_confirm_delete.html'
    success_url = reverse_lazy('pre_agendamento_list')

# View para atualizar o status do pré-agendamento
class PreAgendamentoUpdateStatusView(LoginRequiredMixin, UpdateView):
    model = PreAgendamento
    form_class = PreAgendamentoUpdateStatusForm
    template_name = 'pre_agendamento/pre_agendamento_update_status.html'
    success_url = reverse_lazy('pre_agendamento_list')

    def form_valid(self, form):
        pre_agendamento = form.save(commit=False)
        nova_data_consulta = self.request.POST.get('nova_data_consulta')
        novo_horario = self.request.POST.get('novo_horario')

        if form.cleaned_data['posicao_agendamento'] == '2' and nova_data_consulta and novo_horario:
            pre_agendamento.data_consulta = nova_data_consulta
            pre_agendamento.horario = novo_horario

        pre_agendamento.save()
        return super().form_valid(form)
    
class PreAgendamentoCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'pre_agendamento/pre_agendamento_calendar.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            pre_agendamentos = PreAgendamento.objects.all()
            eventos = [
                {
                    "id": pre_agendamento.id,
                    "title": pre_agendamento.nome,
                    "start": pre_agendamento.data_consulta.strftime('%Y-%m-%dT%H:%M:%S') if pre_agendamento.data_consulta else None,  
                    "extendedProps": {
                        "celular": pre_agendamento.celular,
                        "data_consulta": pre_agendamento.data_consulta.strftime('%d/%m/%Y') if pre_agendamento.data_consulta else "Não informada",
                        "horario": pre_agendamento.horario.strftime('%H:%M') if pre_agendamento.horario else "Não informado",
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


class PreAgendamentoUpdateEventView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            pre_agendamento = get_object_or_404(PreAgendamento, id=data['id'])

            action = data.get('action')

            if action == 'confirmado':
                pre_agendamento.posicao_agendamento = 1  # Confirmado
            elif action == 'reagendado':
                new_date_str = data.get('start')
                if new_date_str:
                    new_date = parse_datetime(new_date_str).date()  # Converte para formato correto (YYYY-MM-DD)
                    pre_agendamento.data_consulta = new_date
                    pre_agendamento.posicao_agendamento = 2  # Reagendado
            elif action == 'desmarcado':
                pre_agendamento.posicao_agendamento = 3  # Desmarcado

            pre_agendamento.save()
            return JsonResponse({
                "success": True,
                "message": "Status atualizado com sucesso.",
                "new_date": pre_agendamento.data_consulta.strftime('%Y-%m-%d'),  # Retorna a nova data
                "posicao_agendamento": pre_agendamento.get_posicao_agendamento_display()
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
# View para exibir relatórios financeiros       
class RelatorioFinanceiroView(LoginRequiredMixin, TemplateView):
    template_name = 'relatorios/relatorio_financeiro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        anos = RegistroAtendimento.objects.dates('data', 'year', order="DESC")
        meses = [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'), (5, 'Maio'),
            (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'), (10, 'Outubro'),
            (11, 'Novembro'), (12, 'Dezembro')
        ]

        ano_selecionado = self.request.GET.get('ano')
        mes_selecionado = self.request.GET.get('mes')

        try:
            ano_selecionado = int(ano_selecionado) if ano_selecionado else datetime.now().year
            mes_selecionado = int(mes_selecionado) if mes_selecionado else None
        except ValueError:
            ano_selecionado = datetime.now().year
            mes_selecionado = None

        queryset = RegistroAtendimento.objects.filter(
            data__year=ano_selecionado
        ).filter(
            Exists(HistoricoProcedimentos.objects.filter(atendimento=OuterRef('pk')))
        )

        valores_parcelados = defaultdict(float)
        total_parcelado_geral = 0.0

        for atendimento in queryset.filter(parcelas__gt=1):
            parcela_valor = float(atendimento.valor_total / atendimento.parcelas)
            data_parcela = atendimento.data.date()

            for i in range(atendimento.parcelas):
                data_mensal = data_parcela + timedelta(days=30 * i)

                if data_mensal.year == ano_selecionado:
                    mes = data_mensal.month
                    valores_parcelados[mes] += parcela_valor

            total_parcelado_geral += float(atendimento.valor_total)

        valores_parcelados_json = json.dumps({int(k): v for k, v in valores_parcelados.items()})

        valor_parcelado_filtro = valores_parcelados.get(mes_selecionado, 0) if mes_selecionado else total_parcelado_geral

        if mes_selecionado:
            queryset = queryset.filter(data__month=mes_selecionado)

        total_atendimentos = queryset.count()
        total_arrecadado = float(queryset.aggregate(total=Sum('valor_pago'))['total'] or 0)
        total_pendente = float(queryset.aggregate(pendente=Sum(F('valor_total') - F('valor_pago')))['pendente'] or 0)

        total_arrecadado_por_mes = defaultdict(float)
        total_atendimentos_por_mes = defaultdict(int)
        total_pendentes_por_mes = defaultdict(float)

        for registro in queryset:
            mes = registro.data.month
            total_arrecadado_por_mes[mes] += float(registro.valor_pago)
            total_atendimentos_por_mes[mes] += 1
            total_pendentes_por_mes[mes] += float(registro.valor_total - registro.valor_pago)

        arrecadado_json = json.dumps({int(k): v for k, v in total_arrecadado_por_mes.items()})
        atendimentos_json = json.dumps({int(k): v for k, v in total_atendimentos_por_mes.items()})
        pendentes_json = json.dumps({int(k): v for k, v in total_pendentes_por_mes.items()})

        context.update({
            'total_atendimentos': total_atendimentos,
            'total_arrecadado': total_arrecadado,
            'total_pendente': total_pendente,
            'valor_parcelado_filtro': valor_parcelado_filtro,
            'anos': [a.year for a in anos],
            'meses': meses,
            'ano_selecionado': ano_selecionado,
            'mes_selecionado': mes_selecionado,
            'valores_parcelados_json': valores_parcelados_json,
            'arrecadado_json': arrecadado_json,
            'atendimentos_json': atendimentos_json,
            'pendentes_json': pendentes_json,
        })

        return context
    
    
class ExportarHistoricoExcelView(View):
    def get(self, request, *args, **kwargs):
        atendimentos = HistoricoProcedimentos.objects.select_related('cliente', 'procedimento', 'profissional', 'atendimento')
        
        # Criando a lista de dados
        dados = []
        for atendimento in atendimentos:
            dados.append({
                "Nome": atendimento.cliente.name,
                "CPF": atendimento.cliente.cpf,
                "Procedimento": atendimento.procedimento.nome,
                "Profissional": atendimento.profissional.nome,
                "Data do Atendimento": atendimento.atendimento.data.strftime('%d/%m/%Y %H:%M'),
                "Valor Pago": float(atendimento.atendimento.valor_pago),
                "Valor Faltante": float(atendimento.valor_faltante()),
                "Forma de Pagamento": atendimento.atendimento.forma_pagamento,
                "Parcelas": atendimento.atendimento.parcelas if atendimento.atendimento.forma_pagamento == "Cartão de Crédito" else "-",
            })
        
        # Criando DataFrame
        df = pd.DataFrame(dados)
        
        # Criando resposta HTTP com o tipo de arquivo correto
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=historico_atendimentos.xlsx'
        
        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Histórico', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Histórico']
            
            # Formatando o cabeçalho
            header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#007bff', 'font_color': 'white', 'border': 1})
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Ajustando colunas automaticamente
            for col_num, col_name in enumerate(df.columns):
                max_length = max(df[col_name].astype(str).map(len).max(), len(col_name)) + 2
                worksheet.set_column(col_num, col_num, max_length)
            
            # Formatação de moeda para valores
            currency_format = workbook.add_format({'num_format': 'R$#,##0.00', 'border': 1})
            valor_pago_col = df.columns.get_loc("Valor Pago")
            valor_faltante_col = df.columns.get_loc("Valor Faltante")
            worksheet.set_column(valor_pago_col, valor_pago_col, 15, currency_format)
            worksheet.set_column(valor_faltante_col, valor_faltante_col, 15, currency_format)
            
        return response