from clientes.models import RegistroClientes, HistoricoClientes
from django.utils.timezone import now

def migrar_clientes_para_historico():
    clientes = RegistroClientes.objects.all()

    for cliente in clientes:
        try:
            historico = HistoricoClientes.objects.filter(cliente=cliente).last()
            
            if not historico:
                historico = HistoricoClientes(
                    cliente=cliente,
                    acao=cliente.acao,
                    tipo_cliente=cliente.tipo_cliente,
                    ultima_atualizacao=cliente.updated_at or now()
                )
                historico.save()
                print(f'✅ Cliente {cliente.name} migrado para o histórico com sucesso!')
        except Exception as e:
            print(f'❌ Erro ao migrar o cliente {cliente.name}: {e}')

# Executar a migração
migrar_clientes_para_historico()
