from django.db import models

# Registro de Clientes
class RegistroClientes(models.Model):
    ORIGEM_ACOES = [
        ("google", "Google"),
        ("facebook", "Facebook"),
        ("formulario", "Formulário"),
        ("instagram", "Instagram"),
        ("amigo", "Amigo"),
        ("parente", "Parente"),
        ("outros", "Outros"),
    ]

    TIPO_CLIENTE = [
        ("estetica", "Somente Estética"),
        ("plastica", "Somente Plástica"),
        ("ambos", "Plástica e Estética"),
    ]

    SEXO_CHOICES = [
        ("masculino", "Masculino"),
        ("feminino", "Feminino"),
        ("nao_dizer", "Prefiro não dizer"),
    ]   

    FORMACAO_CHOICES = [
        ("primaria", "Primária"),
        ("secundaria", "Secundária"),
        ("superior", "Superior"),
    ]

    ESTADO_CIVIL_CHOICES = [
        ("solteiro", "Solteiro(a)"),
        ("casado", "Casado(a)"),
        ("divorciado", "Divorciado(a)"),
        ("viuvo", "Viúvo(a)"),
        ("uniao_estavel", "União Estável"),
        ("outros", "Outros"),
    ]

    name = models.CharField(max_length=400, verbose_name="Nome Completo")  # Campo obrigatório
    d_nasc = models.DateField(verbose_name="Data de Nascimento", blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF", blank=True, null=True)
    telefone = models.CharField(max_length=15, verbose_name="Telefone", blank=True, null=True)
    telefone2 = models.CharField(max_length=15, verbose_name="Telefone Secundário", blank=True, null=True)
    endereco = models.CharField(max_length=300, verbose_name="Endereço", blank=True, null=True)
    numero = models.CharField(max_length=10, verbose_name="Número", blank=True, null=True)
    complemento = models.CharField(max_length=100, verbose_name="Complemento", blank=True, null=True)
    bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    estado = models.CharField(max_length=50, verbose_name="Estado", blank=True, null=True)
    cep = models.CharField(max_length=9, verbose_name="CEP", blank=True, null=True)
    rg = models.CharField(max_length=20, verbose_name="RG", blank=True, null=True)
    sexo = models.CharField(max_length=15, choices=SEXO_CHOICES, verbose_name="Sexo", blank=True, null=True)
    formacao = models.CharField(max_length=15, choices=FORMACAO_CHOICES, verbose_name="Formação", blank=True, null=True)
    ocupacao = models.CharField(max_length=100, verbose_name="Ocupação/Função", blank=True, null=True)
    plano_saude = models.BooleanField(default=False, verbose_name="Possui Plano de Saúde?")
    nome_plano = models.CharField(max_length=150, verbose_name="Nome do Plano de Saúde", blank=True, null=True)
    email = models.EmailField(max_length=150, verbose_name="E-mail", blank=True, null=True)
    acao = models.CharField(max_length=50, choices=ORIGEM_ACOES, verbose_name="Ação de Origem", default="instagram", blank=True, null=True)
    por_quem = models.CharField(max_length=255, verbose_name="Por quem?", blank=True, null=True)
    tipo_cliente = models.CharField(max_length=50, choices=TIPO_CLIENTE, verbose_name="Tipo de Cliente", default="estetica", blank=True, null=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, verbose_name="Estado Civil", default="solteiro", blank=True, null=True)
    restricao = models.TextField(verbose_name="Restrições", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")


    class Meta:
        ordering = ['name']
        verbose_name = "Registro de Cliente"
        verbose_name_plural = "Registros de Clientes"

    def __str__(self):
        return self.name


# Histórico de Clientes
class HistoricoClientes(models.Model):
    cliente = models.ForeignKey(RegistroClientes, on_delete=models.CASCADE, related_name="historico")
    consulta_em = models.DateField(auto_now_add=True, verbose_name="Consultado em")
    acao = models.CharField(max_length=255, verbose_name="Ação Realizada", blank=True, null=True)
    tipo_cliente = models.CharField(
        max_length=50,
        verbose_name="Tipo de Cliente",
        default="estetica"  # Valor padrão para registros antigos
    )
    ultima_atualizacao = models.DateTimeField(null=True, blank=True, verbose_name="Última Atualização")

    class Meta:
        ordering = ['-consulta_em']
        verbose_name = "Histórico de Cliente"
        verbose_name_plural = "Históricos de Clientes"

    def __str__(self):
        return f"Histórico - {self.cliente.name} - {self.consulta_em.strftime('%d/%m/%Y %H:%M:%S')} - {self.tipo_cliente}"
