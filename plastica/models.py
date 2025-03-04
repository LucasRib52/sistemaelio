from django.db import models
from clientes.models import RegistroClientes

# Profissionais de Plástica
class ProfissionalPlastica(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    especialidade = models.CharField(max_length=200, blank=True, null=True, verbose_name="Especialidade")
    telefone = models.CharField(max_length=15, verbose_name="Telefone")  # Agora é obrigatório
    email = models.EmailField(verbose_name="E-mail")  # Agora é obrigatório
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name="Atualizado em")

    def __str__(self):
        return self.nome


# Procedimentos de Plástica
class ProcedimentosPlastica(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    preco_base = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.nome


# Registro de Atendimento Plástica
class RegistroAtendimentoPlastica(models.Model):
    cliente = models.ForeignKey(
        RegistroClientes, on_delete=models.SET_NULL, null=True, blank=True, related_name="atendimentos_plastica"
    )
    procedimento = models.CharField(max_length=255)  # Agora é um texto livre
    profissional = models.ForeignKey(
        ProfissionalPlastica, on_delete=models.SET_NULL, null=True, blank=True, related_name="atendimentos_plastica"
    )
    data = models.DateTimeField()
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    FORMA_PAGAMENTO_CHOICES = [
        ("Dinheiro", "Dinheiro"),
        ("Cartão de Crédito", "Cartão de Crédito"),
        ("Cartão de Débito", "Cartão de Débito"),
        ("Pix", "Pix"),
        ("Outro", "Outro"),
        ("Cortesia", "Cortesia"),  # ✅ Adicionada opção "Cortesia"
    ]

    forma_pagamento = models.CharField(max_length=100, choices=FORMA_PAGAMENTO_CHOICES)
    parcelas = models.IntegerField(default=1, blank=True, null=True)  # ✅ Adicionado campo de parcelas
    descricao = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-data']

    def save(self, *args, **kwargs):
        """
        - Se a forma de pagamento for "Cortesia", zera os valores.
        - Se for "Cartão de Crédito", mantém pelo menos 1 parcela.
        """
        if self.forma_pagamento == "Cortesia":
            self.valor_pago = 0.00
            self.parcelas = None  # Não faz sentido parcelamento em cortesia

        if self.forma_pagamento == "Cartão de Crédito" and (self.parcelas is None or self.parcelas < 1):
            self.parcelas = 1  # Garante que sempre terá pelo menos 1 parcela

        super().save(*args, **kwargs)

    def status_pagamento(self):
        return "Pago" if self.valor_pago > 0 else "Pendente"  # ✅ Corrigido para não usar `valor_total`

    def __str__(self):
        return f"Atendimento {self.id} - {self.cliente}"



# Histórico de Procedimentos de Plástica
class HistoricoProcedimentosPlastica(models.Model):
    cliente = models.ForeignKey(
        RegistroClientes, on_delete=models.CASCADE, related_name="historico_procedimentos_plastica"
    )
    atendimento = models.ForeignKey(
        RegistroAtendimentoPlastica, on_delete=models.CASCADE, related_name="historico_procedimentos_plastica"
    )
    profissional = models.ForeignKey(
        ProfissionalPlastica, on_delete=models.PROTECT, related_name="historico_procedimentos_plastica"
    )
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    procedimento = models.CharField(max_length=255)  # 🆕 Adicionado para evitar erro
    observacoes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def status_pagamento(self):
        return "Pago" if self.preco > 0 else "Pendente"

    def __str__(self):
        return f"{self.atendimento.procedimento} - {self.cliente} - {self.status_pagamento()}"


class PreAgendamentoPlastica(models.Model): 
    nome = models.CharField(max_length=200)  
    celular = models.CharField(max_length=15)  
    data_agendamento = models.DateField()  
    data_consulta = models.DateField()  
    horario = models.TimeField()  
    procedimento = models.CharField(max_length=255)  # Agora é um texto livre

    STATUS_CHOICES = [
        (1, 'Confirmado'),
        (2, 'Reagendado'),
        (3, 'Cancelado'),
        (4, 'Sem Resposta'),
    ]
    
    posicao_agendamento = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=4)
    observacoes = models.TextField(blank=True, null=True)

    cliente = models.ForeignKey(RegistroClientes, on_delete=models.SET_NULL, null=True, blank=True, related_name="agendamentos_plastica")


    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        ordering = ['data_consulta', 'horario']

    def __str__(self):
        return f"Pré-agendamento {self.nome} - {self.procedimento} - {self.data_agendamento.strftime('%d/%m/%Y')}"


# Contratos de Plástica
class ContratoPlastica(models.Model):
    STATUS_CONTRATO = [
        (1, 'Sem Contrato'),
        (2, 'Com Contrato'),
        (3, 'Contrato Finalizado'),
        (4, 'Contrato Cancelado'),
    ]

    cliente = models.ForeignKey(
        RegistroClientes, on_delete=models.PROTECT, related_name="contratos_plastica"
    )
    celular = models.CharField(max_length=15)
    procedimento = models.TextField()
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_contrato = models.DateField(null=True, blank=True)
    data_efetivacao = models.DateField(null=True, blank=True)
    data_validade = models.DateField(null=True, blank=True)
    contrato_assinado = models.ImageField(upload_to="contratos_assinados/", null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CONTRATO, default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def total_pago(self):
        """Calcula o total pago somando os pagamentos associados ao contrato."""
        return sum(p.valor for p in self.pagamentos.all())

    def valor_faltante(self):
        """Calcula o valor faltante do contrato."""
        return max(self.valor_total - self.total_pago(), 0) if self.valor_total else 0

    def atualizar_status(self):
        """Atualiza o status do contrato com base no valor total e nos pagamentos."""
        if self.total_pago() >= self.valor_total:
            self.status = 3  # Contrato Finalizado
        self.save()

    def __str__(self):
        return f"Contrato {self.id} - {self.cliente.nome} - {self.get_status_display()}"


class PagamentoContrato(models.Model):
    """Registro de pagamentos feitos para um contrato."""
    contrato = models.ForeignKey(
        "ContratoPlastica", on_delete=models.CASCADE, related_name="pagamentos"
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateField(null=True, blank=True)
    comprovante = models.FileField(upload_to="comprovantes/", null=True, blank=True)  # ✅ Adicione este campo

    def save(self, *args, **kwargs):
        """Salva o pagamento e atualiza o status do contrato."""
        super().save(*args, **kwargs)
        self.contrato.atualizar_status()

    def __str__(self):
        return f"Pagamento de R$ {self.valor} para {self.contrato.cliente.nome}"
    

