from django import forms
from django.core.validators import RegexValidator
from .models import RegistroClientes

class RegistroClientesForm(forms.ModelForm):
    cpf = forms.CharField(
        max_length=14,
        min_length=14,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control cpf-mask',
            'placeholder': 'CPF XXX.XXX.XXX-XX'
        }),
        validators=[RegexValidator(
            r'^\d{3}\.\d{3}\.\d{3}\-\d{2}$',
            'O CPF deve estar no formato XXX.XXX.XXX-XX.'
        )],
        error_messages={
            'required': 'O CPF é obrigatório.',
            'max_length': 'O CPF deve ter exatamente 14 caracteres (com formatação).',
            'min_length': 'O CPF deve ter exatamente 14 caracteres (com formatação).',
        }
    )

    rg = forms.CharField(
        max_length=13,
        min_length=13,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control rg-mask',
            'placeholder': 'RG XXX.XXX.XXX-X'
        }),
        validators=[RegexValidator(
            r'^\d{3}\.\d{3}\.\d{3}\-\d{1}$',
            'O RG deve estar no formato XXX.XXX.XXX-X.'
        )],
        error_messages={
            'required': 'O RG é obrigatório.',
            'max_length': 'O RG deve ter exatamente 13 caracteres (com formatação).',
            'min_length': 'O RG deve ter exatamente 13 caracteres (com formatação).',
        }
    )

    telefone = forms.CharField(
        max_length=15,
        min_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control telefone-mask',
            'placeholder': 'FONE (XX) XXXXX-XXXX'
        }),
        validators=[RegexValidator(
            r'^\(\d{2}\) \d{5}\-\d{4}$',
            'O telefone deve estar no formato (XX) XXXXX-XXXX.'
        )],
        error_messages={
            'required': 'O telefone é obrigatório.',
            'max_length': 'O telefone deve ter exatamente 15 caracteres (com formatação).',
            'min_length': 'O telefone deve ter exatamente 15 caracteres (com formatação).',
        }
    )

    telefone2 = forms.CharField(
        max_length=15,
        min_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control telefone-mask',
            'placeholder': 'FONE (XX) XXXXX-XXXX'
        }),
        validators=[RegexValidator(
            r'^\(\d{2}\) \d{5}\-\d{4}$',
            'O telefone deve estar no formato (XX) XXXXX-XXXX.'
        )],
    )

    cep = forms.CharField(
        max_length=9,
        min_length=9,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control cep-mask',
            'placeholder': 'CEP XXXXX-XXX'
        }),
        validators=[RegexValidator(
            r'^\d{5}\-\d{3}$',
            'O CEP deve estar no formato XXXXX-XXX.'
        )],
        error_messages={
            'required': 'O CEP é obrigatório.',
            'max_length': 'O CEP deve ter exatamente 9 caracteres (com formatação).',
            'min_length': 'O CEP deve ter exatamente 9 caracteres (com formatação).',
        }
    )

    tipo_cliente = forms.ChoiceField(
        choices=[
            ("estetica", "Somente Estética"),
            ("plastica", "Somente Plástica"),
            ("ambos", "Plástica e Estética"),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    numero = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número'
        }),
        validators=[RegexValidator(
            r'^\d+$',
            'O número deve conter apenas dígitos.'
        )],
        error_messages={
            'required': 'O número do endereço é obrigatório.',
            'max_length': 'O número deve ter no máximo 6 dígitos.',
        }
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o e-mail'
        }),
        error_messages={
            'required': 'O e-mail é obrigatório.',
            'invalid': 'Digite um endereço de e-mail válido.',
        }
    )

    class Meta:
        model = RegistroClientes
        fields = [
            'name', 'd_nasc', 'cpf', 'telefone', 'telefone2', 'endereco', 'numero',
            'complemento', 'bairro', 'cidade', 'estado', 'cep', 'rg', 'sexo', 'formacao',
            'ocupacao', 'plano_saude', 'email', 'acao','por_quem', 'tipo_cliente', 'estado_civil',
            'restricao', 'nome_plano'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome completo'
            }),
            'd_nasc': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o endereço'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complemento'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade'
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estado'
            }),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'formacao': forms.Select(attrs={'class': 'form-select'}),
            'ocupacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a ocupação/função'
            }),
            'plano_saude': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nome_plano': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do plano'
            }),
            'acao': forms.Select(attrs={'class': 'form-select'}),
            'por_quem': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Informe quem indicou'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'restricao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Digite as Observações/Restrições',
                'rows': 3
            }),
        }

    def clean_tipo_cliente(self):
        tipo_cliente = self.cleaned_data.get("tipo_cliente")
        print("DEBUG: Valor do tipo_cliente no formulário:", tipo_cliente)
        if tipo_cliente not in ["estetica", "plastica", "ambos"]:
            raise forms.ValidationError("Tipo de cliente inválido!")
        return tipo_cliente
