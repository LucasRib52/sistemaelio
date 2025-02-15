from clientes.models import RegistroClientes, HistoricoClientes
import pandas as pd
from datetime import datetime

def excluir_todos_clientes():
    HistoricoClientes.objects.all().delete()  # Excluir históricos primeiro
    RegistroClientes.objects.all().delete()  # Excluir clientes depois
    print("🗑️ Todos os clientes e históricos foram excluídos com sucesso.")

def importar_clientes(file_path):
    df = pd.read_excel(file_path)
    df.columns = [str(col).strip().replace('\t', '').replace('.', '') for col in df.columns]

    sexo_map = {'F': 'feminino', 'M': 'masculino'}
    estado_civil_map = {
        'Solteira': 'solteiro', 'Solteiro': 'solteiro',
        'Casada': 'casado', 'Casado': 'casado',
        'Divorciada': 'divorciado', 'Divorciado': 'divorciado',
        'Viúva': 'viuvo', 'Viúvo': 'viuvo'
    }

    for index, row in df.iterrows():
        try:
            # Garantir que valores NaN sejam tratados corretamente
            plastica = row.get('plastica')
            estetica = row.get('estetica')

            # Tratamento para substituir NaN por None
            plastica = None if pd.isna(plastica) else int(plastica)
            estetica = None if pd.isna(estetica) else int(estetica)

            # Correção da lógica do tipo_cliente
            if plastica == 0 and estetica is None:  
                tipo_cliente = 'plastica'
            elif plastica is None and estetica == 1:  
                tipo_cliente = 'estetica'
            elif plastica == 0 and estetica == 1:  
                tipo_cliente = 'ambos'
            else:
                tipo_cliente = 'plastica'  # Valor padrão

            d_nasc = row.get('d_nasc')
            if pd.notna(d_nasc):
                try:
                    if isinstance(d_nasc, str):
                        d_nasc = datetime.strptime(d_nasc, '%d/%m/%Y').date()
                    else:
                        d_nasc = pd.to_datetime(d_nasc, errors='coerce').date()
                except Exception:
                    d_nasc = datetime.strptime('1900-01-01', '%Y-%m-%d').date()
            else:
                d_nasc = datetime.strptime('1900-01-01', '%Y-%m-%d').date()

            cpf = str(row.get('cpf', '')).strip()
            cpf = ''.join(filter(str.isdigit, cpf)) if cpf else f"{str(index).zfill(11)}"

            telefone = str(row.get('telefone', '')).strip()
            telefone = ''.join(filter(str.isdigit, telefone))

            telefone2 = str(row.get('telefone2', '')).strip()
            telefone2 = ''.join(filter(str.isdigit, telefone2))

            nome_plano = str(row.get('nome_plano', '')).strip()
            plano_saude = bool(nome_plano)

            if RegistroClientes.objects.filter(cpf=cpf).exists():
                print(f"⚠️ Cliente com CPF {cpf} já existe. Ignorando.")
                continue

            cliente = RegistroClientes(
                name=row.get('name', 'Nome Desconhecido'),
                d_nasc=d_nasc,
                cpf=cpf,
                telefone=telefone,
                telefone2=telefone2,
                endereco=str(row.get('endereco', '')).strip(),
                numero=str(row.get('numero', '')).strip(),
                complemento=str(row.get('complemento', '')).strip(),
                bairro=str(row.get('bairro', '')).strip(),
                cidade=str(row.get('cidade', '')).strip(),
                estado=str(row.get('estado', '')).strip(),
                cep=''.join(filter(str.isdigit, str(row.get('cep', '')))),
                rg=''.join(filter(str.isdigit, str(row.get('rg', '')))),
                sexo=sexo_map.get(row.get('sexo'), 'nao_dizer'),
                formacao='primaria',
                ocupacao=str(row.get('ocupacao', '')).strip(),
                plano_saude=plano_saude,
                nome_plano=nome_plano,
                email=str(row.get('email', '')).strip(),
                acao=row.get('acao', 'outros') if pd.notna(row.get('acao')) else 'outros',
                tipo_cliente=tipo_cliente,
                estado_civil=estado_civil_map.get(row.get('estado_civil'), 'outros'),
                restricao='',
            )
            cliente.save()
            print(f'✅ Cliente {cliente.name} importado com sucesso! - Tipo: {tipo_cliente} - Data: {d_nasc}')

        except Exception as e:
            print(f'❌ Erro ao importar {row.get("name", "desconhecido")} na linha {index+1}: {e}')

# Executar exclusão e importação
excluir_todos_clientes()
importar_clientes('clientes/importacoes/CADSTRO GERAL PROGRAMA.xlsx')
