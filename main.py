
from time import sleep

from colaborabot import Colaborabot


# Guardando informações de hora e data da máquina

DIA = datetime.datetime.now().day
MES = datetime.datetime.now().month
ANO = datetime.datetime.now().year
data = '{:02d}/{:02d}/{:02d}'.format(DIA, MES, ANO) # 11/04/2019


def plan_csv():
    """
    Cria um arquivo local para guardar todas as interações do bot.
    """
    pasta_logs = Path(f'logs')
    arq_log = pasta_logs / f'colaborabot-log-{ANO}-{MES}-{DIA}.csv'
    if not pasta_logs.exists():
        pasta_logs.mkdir()
    arq_log.write_text(data='data_bsb;data_utc;url;orgao;cod_resposta\n', encoding='UTF8')
    return arq_log


if __name__ == '__main__':

    #criando bot
    colaborabot = Colaborabot()

    # cria um arquivo csv para salvar todos as interacoes do bot
    # É TOTALMENTE LOCAL
    #TODO: Colaborabot depende disso
    arq_log = plan_csv()

    # executa analise a cada 300ms
    while True:
        colaborabot.busca_disponibilidade_sites()
        sleep(600)