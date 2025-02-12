from django import forms
from .models import RegistroAtendimento, Procedimentos, Profissional, PreAgendamento

# Formulário para Profissional
class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ['nome', 'especialidade', 'telefone', 'email', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidade': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seuemail@exemplo.com'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    # Tornando nome, telefone e email obrigatórios
    nome = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefone = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seuemail@exemplo.com'}))

# Formulário para Procedimentos
class ProcedimentoForm(forms.ModelForm):
    class Meta:
        model = Procedimentos
        fields = ['nome', 'descricao', 'preco_base',]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do procedimento'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição do procedimento'}),
            'preco_base': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço base'}),
        }


class RegistroAtendimentoForm(forms.ModelForm):
    quantidade_sessoes = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'id_quantidade_sessoes',
            'min': 1,
            'placeholder': 'Digite a quantidade de sessões'
        })
    )

    # 🆕 Campo para número de parcelas (dropdown de 1 a 12)
    parcelas = forms.ChoiceField(
        choices=[(str(i), f"{i}x") for i in range(1, 13)],  # 1x até 12x
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_parcelas'
        })
    )

    class Meta:
        model = RegistroAtendimento
        fields = [
            'cliente', 'procedimento', 'profissional', 'data',
            'valor_total', 'valor_pago', 'forma_pagamento',
            'parcelas',  # 🆕 Adicionado o campo de parcelas
            'descricao', 'quantidade_sessoes'
        ]
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_estetica_cliente',
                'placeholder': 'Digite para buscar um cliente...'
            }),
            'procedimento': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_estetica_procedimento'
            }),
            'profissional': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_estetica_profissional'
            }),
            'data': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'id': 'id_estetica_data'
            }),
            'valor_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_estetica_valor_total',
                'placeholder': 'Digite o valor total'
            }),
            'valor_pago': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_estetica_valor_pago',
                'placeholder': 'Digite o valor pago'
            }),
            'forma_pagamento': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_estetica_forma_pagamento'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'id_estetica_descricao',
                'rows': 3,
                'placeholder': 'Descreva detalhes do atendimento...'
            }),
        }

    def clean(self):
        """
        Validação adicional para calcular e verificar valores faltantes.
        """
        cleaned_data = super().clean()
        valor_total = cleaned_data.get('valor_total', 0)
        valor_pago = cleaned_data.get('valor_pago', 0)
        quantidade_sessoes = cleaned_data.get('quantidade_sessoes', 1)

        if valor_total is not None and valor_pago is not None:
            if valor_pago > valor_total:
                self.add_error('valor_pago', 'O valor pago não pode ser maior que o valor total.')

        if quantidade_sessoes < 1:
            self.add_error('quantidade_sessoes', 'A quantidade de sessões deve ser pelo menos 1.')

        return cleaned_data


class PreAgendamentoForm(forms.ModelForm):
    class Meta:
        model = PreAgendamento
        fields = ['nome', 'celular', 'data_agendamento', 'data_consulta', 'horario', 'procedimento', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Cliente'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular (com DDD)'}),
            'data_agendamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_consulta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horario': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'procedimento': forms.Select(attrs={'class': 'form-control'}),  # Adicionado!
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define automaticamente o status inicial para "Sem Resposta"
        if not self.instance.pk:
            self.instance.posicao_agendamento = 4

    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        celular = celular.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        if not celular.isdigit() or len(celular) not in [10, 11]:
            raise forms.ValidationError("Informe um número de celular válido com DDD.")
        return celular


# Formulário exclusivo para atualização de status
class PreAgendamentoUpdateStatusForm(forms.ModelForm):
    STATUS_CHOICES = [
        (1, 'Confirmado'),
        (2, 'Reagendado'),
        (3, 'Desmarcado'),
        (4, 'Sem Resposta'),
    ]

    posicao_agendamento = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Status do Agendamento"
    )

    class Meta:
        model = PreAgendamento
        fields = ['posicao_agendamento']