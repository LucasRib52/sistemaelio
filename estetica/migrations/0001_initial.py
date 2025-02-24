# Generated by Django 5.1.4 on 2025-02-22 12:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Procedimentos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('preco_base', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profissional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('especialidade', models.CharField(blank=True, max_length=200, null=True)),
                ('telefone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('ativo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PreAgendamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('celular', models.CharField(max_length=15)),
                ('data_agendamento', models.DateField()),
                ('data_consulta', models.DateField()),
                ('horario', models.TimeField()),
                ('posicao_agendamento', models.PositiveSmallIntegerField(choices=[(1, 'Confirmado'), (2, 'Reagendado'), (3, 'Desmarcado'), (4, 'Sem Resposta')], default=4)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agendamentos', to='clientes.registroclientes')),
                ('procedimento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pre_agendamentos', to='estetica.procedimentos')),
            ],
        ),
        migrations.CreateModel(
            name='RegistroAtendimento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField()),
                ('valor_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('valor_pago', models.DecimalField(decimal_places=2, max_digits=10)),
                ('forma_pagamento', models.CharField(choices=[('Dinheiro', 'Dinheiro'), ('Cartão de Crédito', 'Cartão de Crédito'), ('Cartão de Débito', 'Cartão de Débito'), ('Pix', 'Pix'), ('Outro', 'Outro')], max_length=100)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('quantidade_sessoes', models.IntegerField(default=1)),
                ('parcelas', models.IntegerField(blank=True, default=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='atendimentos', to='clientes.registroclientes')),
                ('procedimento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='atendimentos', to='estetica.procedimentos')),
                ('profissional', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='atendimentos', to='estetica.profissional')),
            ],
            options={
                'ordering': ['-data'],
            },
        ),
        migrations.CreateModel(
            name='HistoricoProcedimentos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preco', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantidade_sessoes', models.IntegerField(default=1)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico_procedimentos', to='clientes.registroclientes')),
                ('procedimento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico_procedimentos', to='estetica.procedimentos')),
                ('profissional', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='historico_procedimentos', to='estetica.profissional')),
                ('atendimento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='historico_procedimentos', to='estetica.registroatendimento')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
