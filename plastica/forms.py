from django import forms
from .models import (
    RegistroAtendimentoPlastica,
    ProcedimentosPlastica,
    ProfissionalPlastica,
    PreAgendamentoPlastica,
    ContratoPlastica,
    PagamentoContrato
)

class ProfissionalPlasticaForm(forms.ModelForm):
    class Meta:
        model = ProfissionalPlastica
        fields = ['nome', 'especialidade', 'telefone', 'email', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidade': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seuemail@exemplo.com'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    # Definindo os campos obrigatórios
    telefone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
        error_messages={'required': 'O telefone é obrigatório.'}
    )

    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seuemail@exemplo.com'}),
        error_messages={'required': 'O e-mail é obrigatório.'}
    )

# Formulário para Procedimentos de Plástica
class ProcedimentoPlasticaForm(forms.ModelForm):
    class Meta:
        model = ProcedimentosPlastica
        fields = ['nome', 'descricao', 'preco_base']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preco_base': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Formulário para Registro de Atendimento de Plástica
class RegistroAtendimentoPlasticaForm(forms.ModelForm):
    # ✅ Campo para número de parcelas (aparece apenas para Cartão de Crédito)
    parcelas = forms.ChoiceField(
        choices=[(str(i), f"{i}x") for i in range(1, 13)],  # 1x até 12x
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_parcelas'})
    )

    class Meta:
        model = RegistroAtendimentoPlastica
        fields = [
            'cliente', 'procedimento', 'profissional', 'data',
            'valor_pago', 'forma_pagamento', 'parcelas', 'descricao'  # ✅ Adicionado `parcelas`
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'procedimento': forms.TextInput(attrs={'class': 'form-control'}),  # Alterado para campo de texto
            'profissional': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-control', 'id': 'id_forma_pagamento'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        forma_pagamento = cleaned_data.get("forma_pagamento")
        valor_pago = cleaned_data.get("valor_pago")
        parcelas = cleaned_data.get("parcelas")

        # 🔹 Se a forma de pagamento for "Cortesia", zerar o valor pago e remover parcelas
        if forma_pagamento == "Cortesia":
            cleaned_data["valor_pago"] = 0.00
            cleaned_data["parcelas"] = None

        # 🔹 Se for "Cartão de Crédito", garantir que tenha pelo menos 1 parcela
        if forma_pagamento == "Cartão de Crédito":
            if not parcelas or int(parcelas) < 1:
                cleaned_data["parcelas"] = 1

        return cleaned_data


class PreAgendamentoPlasticaForm(forms.ModelForm):
    class Meta:
        model = PreAgendamentoPlastica
        fields = ['nome', 'celular', 'data_agendamento', 'data_consulta', 'horario', 'procedimento', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Cliente'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular (com DDD)'}),
            'data_agendamento': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'data_consulta': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'horario': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'procedimento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o procedimento'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.instance.posicao_agendamento = 4

    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        celular = celular.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
        if not celular.isdigit() or len(celular) not in [10, 11]:
            raise forms.ValidationError("Informe um número de celular válido com DDD.")
        return celular

class PreAgendamentoPlasticaUpdateStatusForm(forms.ModelForm):
    STATUS_CHOICES = [
        (1, 'Confirmado'),
        (2, 'Reagendado'),
        (3, 'Cancelado'),
        (4, 'Sem Resposta'),
    ]

    posicao_agendamento = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Status do Agendamento"
    )

    class Meta:
        model = PreAgendamentoPlastica
        fields = ['posicao_agendamento']



class ContratoPlasticaForm(forms.ModelForm):
    class Meta:
        model = ContratoPlastica
        fields = [
            'cliente', 'celular', 'procedimento', 'valor_total',
            'data_contrato', 'data_efetivacao', 'data_validade', 
            'contrato_assinado', 'status'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'procedimento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),  # Agora é um campo de texto digitável
            'valor_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_contrato': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_efetivacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_validade': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contrato_assinado': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        

class PagamentoContratoForm(forms.ModelForm):
    class Meta:
        model = PagamentoContrato
        fields = ['valor', 'data_pagamento', 'comprovante']  # ✅ Agora inclui o comprovante
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comprovante': forms.FileInput(attrs={'class': 'form-control'}),  # ✅ Input de arquivo
        }
