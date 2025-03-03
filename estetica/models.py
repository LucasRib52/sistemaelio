from django.db import models
from clientes.models import RegistroClientes


# Profissionais
class Profissional(models.Model):
    nome = models.CharField(max_length=200)  # Nome do profissional
    especialidade = models.CharField(max_length=200, blank=True, null=True)  # Especialidade
    telefone = models.CharField(max_length=15)  # Telefone de contato
    email = models.EmailField()  # Email
    ativo = models.BooleanField(default=True)  # Status do profissional (ativo/inativo)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.nome


# Procedimentos
class Procedimentos(models.Model):
    nome = models.CharField(max_length=200)  # Nome do procedimento
    descricao = models.TextField(blank=True, null=True)  # Descrição
    preco_base = models.DecimalField(max_digits=10, decimal_places=2)  # Preço base do procedimento
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.nome


# Registro de Atendimento
class RegistroAtendimento(models.Model):
    cliente = models.ForeignKey(
        RegistroClientes, on_delete=models.PROTECT, related_name="atendimentos"
    )
    procedimento = models.ForeignKey(
        Procedimentos, on_delete=models.CASCADE, related_name="atendimentos"
    )
    profissional = models.ForeignKey(
        Profissional, on_delete=models.PROTECT, related_name="atendimentos"
    )  # Profissional responsável
    data = models.DateTimeField()  # Data e hora do atendimento
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    forma_pagamento = models.CharField(
        max_length=100,
        choices=[
            ("Dinheiro", "Dinheiro"),
            ("Cartão de Crédito", "Cartão de Crédito"),
            ("Cartão de Débito", "Cartão de Débito"),
            ("Pix", "Pix"),
            ("Outro", "Outro"),
        ],
    )  # Forma de pagamento
    descricao = models.TextField(blank=True, null=True)  # Observações (opcional)
    quantidade_sessoes = models.IntegerField(default=1)  # 🆕 Adicionando o campo quantidade de sessões
    parcelas = models.IntegerField(default=1, blank=True, null=True)  # Número de parcelas (opcional)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-data']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # 🔥 Agora permite atualizar qualquer campo, incluindo valor_pago

    def status_pagamento(self):
        if self.valor_pago >= self.valor_total:
            return "Pago"
        return "Pendente"

    def valor_faltante(self):
        return max(self.valor_total - self.valor_pago, 0)



# Histórico de Procedimentos
class HistoricoProcedimentos(models.Model):
    cliente = models.ForeignKey(
        RegistroClientes, on_delete=models.CASCADE, related_name="historico_procedimentos"
    )
    procedimento = models.ForeignKey(
        Procedimentos, on_delete=models.CASCADE, related_name="historico_procedimentos"
    )
    atendimento = models.ForeignKey(
        RegistroAtendimento, on_delete=models.PROTECT, related_name="historico_procedimentos"
    )
    profissional = models.ForeignKey(
        Profissional, on_delete=models.PROTECT, related_name="historico_procedimentos"
    )
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_sessoes = models.IntegerField(default=1)  # ✅ Pegando corretamente
    observacoes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def status_pagamento(self):
        return self.atendimento.status_pagamento()

    def valor_pago(self):
        return self.atendimento.valor_pago

    def valor_faltante(self):
        return self.atendimento.valor_faltante()

    def __str__(self):
        return f"{self.procedimento.nome} - {self.cliente} ({self.quantidade_sessoes} sessões)"
    
#Pre Agendamento
class PreAgendamento(models.Model):
    nome = models.CharField(max_length=200)  
    celular = models.CharField(max_length=15)  
    data_agendamento = models.DateField()  
    data_consulta = models.DateField()  
    horario = models.TimeField()  
    procedimento = models.ForeignKey(
        Procedimentos, on_delete=models.CASCADE, related_name="pre_agendamentos"
    )  

    STATUS_CHOICES = [
        (1, 'Confirmado'),
        (2, 'Reagendado'),
        (3, 'Cancelado'),
        (4, 'Sem Resposta'),
    ]   
    
    posicao_agendamento = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=4)
    observacoes = models.TextField(blank=True, null=True)

    # Novo campo que relaciona um pré-agendamento a um cliente cadastrado
    cliente = models.ForeignKey(RegistroClientes, on_delete=models.SET_NULL, null=True, blank=True, related_name="agendamentos")


    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Pré-agendamento {self.nome} - {self.procedimento.nome} - {self.data_agendamento.strftime('%d/%m/%Y')}"