from django.contrib import messages
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
import csv
import pandas as pd
import xlsxwriter
from .models import RegistroClientes, HistoricoClientes
from estetica.models import PreAgendamento  # Import correto do app onde está o modelo
from .forms import RegistroClientesForm
from django.db import transaction
from plastica.models import RegistroAtendimentoPlastica

from plastica.models import PreAgendamentoPlastica  # 🔹 Importando o modelo correto

class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = RegistroClientes
    form_class = RegistroClientesForm
    template_name = 'cliente_registro.html'
    success_url = reverse_lazy('clientes_list')

    def form_valid(self, form):
        cliente = form.save(commit=False)

        # Removendo caracteres especiais do CPF e telefone antes de salvar
        cliente.cpf = cliente.cpf.replace('.', '').replace('-', '')
        cliente.telefone = cliente.telefone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')

        cliente.save()

        # Criar entrada no histórico de clientes
        HistoricoClientes.objects.create(
            cliente=cliente,
            acao="Cadastro realizado com sucesso",
            tipo_cliente=cliente.tipo_cliente
        )

        # Vincular pré-agendamento ao cliente, se existir um correspondente
        nome = self.request.GET.get('nome')
        celular = self.request.GET.get('celular')

        if nome and celular:
            # 🔹 Buscar pré-agendamentos em Estética
            pre_agendamentos = PreAgendamento.objects.filter(nome=nome, celular=celular, cliente__isnull=True)
            for pre_agendamento in pre_agendamentos:
                pre_agendamento.cliente = cliente
                pre_agendamento.save()

            # 🔹 Buscar pré-agendamentos em Plástica
            pre_agendamentos_plastica = PreAgendamentoPlastica.objects.filter(nome=nome, celular=celular, cliente__isnull=True)
            for pre_agendamento in pre_agendamentos_plastica:
                pre_agendamento.cliente = cliente
                pre_agendamento.save()

        messages.success(self.request, 'Cliente registrado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao registrar cliente. Verifique os campos e tente novamente.')
        return self.render_to_response(self.get_context_data(form=form))

# View para visualizar detalhes do cliente
class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = RegistroClientes
    template_name = 'cliente_view.html'
    context_object_name = 'cliente'
    
# View para listar os históricos de clientes com filtros
class ClienteListView(LoginRequiredMixin, ListView):
    model = HistoricoClientes
    template_name = 'cliente_historico.html'
    context_object_name = 'historicos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        tipo_cliente = self.request.GET.get('tipo_cliente')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        order_by = self.request.GET.get('order_by', '-consulta_em')

        if query:
            queryset = queryset.filter(cliente__name__icontains=query) | queryset.filter(cliente__cpf__icontains=query)

        if tipo_cliente and tipo_cliente != 'ambos':
            queryset = queryset.filter(tipo_cliente=tipo_cliente)

        if data_inicio and data_fim:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d").date()
                data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d").date()
                queryset = queryset.filter(consulta_em__date__range=[data_inicio_obj, data_fim_obj])
            except ValueError:
                pass

        # Valida ordenação para evitar injeção de dados indesejados
        valid_fields = ['cliente__name', 'consulta_em', 'cliente__cpf', 'ultima_atualizacao']
        if order_by.lstrip('-') not in valid_fields:
            order_by = '-consulta_em'

        return queryset.order_by(order_by)

# View para editar os dados do cliente
class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = RegistroClientes
    form_class = RegistroClientesForm
    template_name = 'cliente_editar.html'
    success_url = reverse_lazy('clientes_list')

    def form_valid(self, form):
        cliente = form.save(commit=False)

        # Sanitizando os dados antes de salvar
        cliente.cpf = cliente.cpf.replace('.', '').replace('-', '')
        cliente.telefone = cliente.telefone.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')

        cliente.save()

        # Buscar se já existe um histórico para esse cliente
        historico, created = HistoricoClientes.objects.get_or_create(
            cliente=cliente,
            defaults={'acao': "Última atualização", 'tipo_cliente': cliente.tipo_cliente, 'ultima_atualizacao': datetime.now()}
        )

        # Se o histórico já existia, apenas atualizar a data de última atualização
        if not created:
            historico.ultima_atualizacao = datetime.now()
            historico.save()

        messages.success(self.request, "Os dados do cliente foram atualizados com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao atualizar os dados do cliente. Verifique os campos e tente novamente.")
        return self.render_to_response(self.get_context_data(form=form))

# View para excluir histórico de clientes
class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = RegistroClientes
    template_name = 'cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes_list')

    def delete(self, request, *args, **kwargs):
        cliente = self.get_object()

        with transaction.atomic():
            # Deleta todos os atendimentos plásticos associados ao cliente
            RegistroAtendimentoPlastica.objects.filter(cliente=cliente).delete()
            # Agora, pode deletar o cliente sem erro
            messages.success(request, "Cliente excluído com sucesso.")
            return super().delete(request, *args, **kwargs)

# Função para exportar histórico de clientes em CSV
class ExportarClientesExcelView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        clientes = RegistroClientes.objects.all()
        
        # Criando a lista de dados
        dados = []
        for cliente in clientes:
            dados.append({
                "Nome": cliente.name,
                "Tipo de Cliente": cliente.get_tipo_cliente_display(),
                "Data de Nascimento": cliente.d_nasc.strftime('%d/%m/%Y') if cliente.d_nasc else "",
                "CPF": cliente.cpf,
                "RG": cliente.rg,
                "Telefone": cliente.telefone,
                "Telefone Secundário": cliente.telefone2 if cliente.telefone2 else "",
                "Email": cliente.email,
                "Sexo": cliente.get_sexo_display(),
                "Estado Civil": cliente.get_estado_civil_display(),
                "Formação": cliente.get_formacao_display(),
                "Ocupação/Função": cliente.ocupacao if cliente.ocupacao else "",
                "CEP": cliente.cep,
                "Endereço": cliente.endereco,
                "Número": cliente.numero,
                "Complemento": cliente.complemento if cliente.complemento else "",
                "Bairro": cliente.bairro,
                "Cidade": cliente.cidade,
                "Estado": cliente.estado,
                "Veio através de": cliente.get_acao_display(),
                "Possui Plano de Saúde": "Sim" if cliente.plano_saude else "Não",
                "Nome do Plano de Saúde": cliente.nome_plano if cliente.nome_plano else "",
                "Restrições": cliente.restricao if cliente.restricao else "",
                
            })
        
        # Criando DataFrame
        df = pd.DataFrame(dados)
        
        # Criando resposta HTTP com o tipo de arquivo correto
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=clientes_registrados.xlsx'
        
        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Clientes', index=False)
            workbook = writer.book
            worksheet = writer.sheets['Clientes']
            
            # Formatando o cabeçalho
            header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#007bff', 'font_color': 'white', 'border': 1})
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Ajustando colunas automaticamente
            for col_num, col_name in enumerate(df.columns):
                max_length = max(df[col_name].astype(str).map(len).max(), len(col_name)) + 2
                worksheet.set_column(col_num, col_num, max_length)
        
        return response
