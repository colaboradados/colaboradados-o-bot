
from time import sleep

from colaborabot import Colaborabot

# não é utilizado??
# def criar_tweet(url, orgao):
#     """
#     Criando o tweet com o status do site recém acessado
#     """
#     twitter_bot.update_status(lista_frases(url=url, orgao=orgao))

# Guardando informações de hora e data da máquina

DIA = datetime.datetime.now().day
MES = datetime.datetime.now().month
ANO = datetime.datetime.now().year
data = '{:02d}/{:02d}/{:02d}'.format(DIA, MES, ANO) # 11/04/2019

def plan_gs(dia, mes, ano):
    """
    Cria planilha no Google Drive, envia por e-mail e preenche o cabeçalho (data e hora no fuso horário de Brasília,
    data e hora no UTC, url afetada, órgão responsável e código de resposta do acesso).
    A planilha criada possui as permissões de leitura para qualquer pessoa com o link, porém somente a conta da API do
    bot (que não é a mesma conta usada pela equipe) consegue alterar os dados contidos nela.

    Também é acessado uma planilha índice (docs.google.com/spreadsheets/d/1kIwjn2K0XKAOWZLVRBx9lOU5D4TTUanvmhzmdx7bh0w)
    e incluído a planilha de logs nela, na segunda tabela.
    """

    lista_planilhas = []
    todas_planilhas = google_drive_creds.list_spreadsheet_files()

    for item in todas_planilhas:
        lista_planilhas.append(item['name'])

    if f'colaborabot-sites-offline-{dia:02d}{mes:02d}{ano:04d}' not in lista_planilhas:
        planilha = google_drive_creds.create(f'colaborabot-sites-offline-{dia:02d}{mes:02d}{ano:04d}')  # Exemplo de nome final: colaborabot-sites-offline-27022019
        cabecalho = planilha.get_worksheet(index=0)
        cabecalho.insert_row(values=['data_bsb', 'data_utc', 'url', 'orgao', 'cod_resposta'])
        
        plan_indice = google_drive_creds.open_by_key('1kIwjn2K0XKAOWZLVRBx9lOU5D4TTUanvmhzmdx7bh0w')
        tab_indice = plan_indice.get_worksheet(index=1)
        endereco = f'docs.google.com/spreadsheets/d/{planilha.id}/'
        tab_indice.append_row(values=[data, endereco])

    else:
        planilha = google_drive_creds.open(title=f'colaborabot-sites-offline-{dia:02d}{mes:02d}{ano:04d}')

    sleep(5)
    planilha.share(None, perm_type='anyone', role='reader')
    print(f'https://docs.google.com/spreadsheets/d/{planilha.id}\n')
    return planilha

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

    # Criando publicadores
    # responsabilidade do publicador dentro do colaborabot
    # mastodon_bot = masto_auth()
    # twitter_bot = twitter_auth()

    # utilizado para acessar uma tabela
    google_drive_creds = google_sshet()

    # cria planilha do google drive como se fosse um LOG de cada erro que o bot encontra em cada site
    planilha_google = plan_gs(dia=DIA, mes=MES, ano=ANO)

    # cria um arquivo csv para salvar todos as interacoes do bot
    arq_log = plan_csv()

    # executa analise a cada 300ms
    while True:
        colaborabot.busca_disponibilidade_sites()
        sleep(600)