from django import forms
from .models import RegistroClientes
from django.core.validators import RegexValidator

class RegistroClientesForm(forms.ModelForm):
    cpf = forms.CharField(
        max_length=11,
        min_length=11,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CPF'}),
        validators=[RegexValidator(r'^\d{11}$', 'O CPF deve conter exatamente 11 dígitos numéricos.')],
        error_messages={
            'required': 'O CPF é obrigatório.',
            'max_length': 'O CPF deve ter exatamente 11 números.',
            'min_length': 'O CPF deve ter exatamente 11 números.',
        }
    )

    rg = forms.CharField(
        max_length=9,
        min_length=9,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o RG'}),
        validators=[RegexValidator(r'^\d{9}$', 'O RG deve conter exatamente 9 dígitos numéricos.')],
        error_messages={
            'required': 'O RG é obrigatório.',
            'max_length': 'O RG deve ter exatamente 9 números.',
            'min_length': 'O RG deve ter exatamente 9 números.',
        }
    )

    telefone = forms.CharField(
        max_length=11,
        min_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o telefone'}),
        validators=[RegexValidator(r'^\d{10,11}$', 'O telefone deve ter 10 ou 11 dígitos.')],
        error_messages={
            'required': 'O telefone é obrigatório.',
            'max_length': 'O telefone deve ter no máximo 11 números.',
            'min_length': 'O telefone deve ter no mínimo 10 números.',
        }
    )

    telefone2 = forms.CharField(
        max_length=11,
        min_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o telefone secundário'}),
        validators=[RegexValidator(r'^\d{10,11}$', 'O telefone deve ter 10 ou 11 dígitos.')],
    )

    numero = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
        validators=[RegexValidator(r'^\d+$', 'O número deve conter apenas dígitos.')],
        error_messages={
            'required': 'O número do endereço é obrigatório.',
            'max_length': 'O número deve ter no máximo 6 dígitos.',
        }
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite o e-mail'}),
        error_messages={
            'required': 'O e-mail é obrigatório.',
            'invalid': 'Digite um endereço de e-mail válido.',
        }
    )

    class Meta:
        model = RegistroClientes
        fields = [
            'name', 'd_nasc', 'cpf', 'telefone', 'telefone2', 'endereco', 'numero', 'complemento', 
            'bairro', 'cidade', 'estado', 'cep', 'rg', 'sexo', 'formacao', 'ocupacao', 'plano_saude', 
            'email', 'acao', 'tipo_cliente', 'estado_civil', 'restricao', 'nome_plano'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome completo'}),
            'd_nasc': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o endereço'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complemento'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CEP'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'formacao': forms.Select(attrs={'class': 'form-select'}),
            'ocupacao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite a ocupação/função'}),
            'plano_saude': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nome_plano': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome do plano'}),
            'acao': forms.Select(attrs={'class': 'form-select'}),
            'tipo_cliente': forms.Select(attrs={'class': 'form-select'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'restricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Digite as restrições', 'rows': 3}),
        }
