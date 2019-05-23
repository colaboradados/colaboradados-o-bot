# Importando as libraries

import csv
import datetime
import json
from pathlib import Path
from time import sleep

from requests import get, exceptions

import settings
from autenticadores import twitter_auth, google_api_auth, masto_auth
from divulga import lista_frases, checar_timelines, google_sshet

# Parametros de acesso das urls

headers = {
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

TOTAL_TENTATIVAS = 10
STATUS_SUCESSO = 200

# Guardando informações de hora e data da máquina

DIA = datetime.datetime.now().day
MES = datetime.datetime.now().month
ANO = datetime.datetime.now().year

data = '{:02d}/{:02d}/{:02d}'.format(DIA, MES, ANO) # 11/04/2019


def criar_tweet(url, orgao):
    """
    Criando o tweet com o status do site recém acessado
    """
    twitter_bot.update_status(lista_frases(url=url, orgao=orgao))


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


def cria_dados(url, portal, resposta):
    """
    Captura as informações de hora e data da máquina, endereço da página e
    resposta recebida e as prepara dentro de uma lista para inserir na tabela.
    """

    momento = str(json.dumps(datetime.datetime.now().isoformat(sep=' ', timespec='seconds'), indent=4, sort_keys=True, default=str))
    momento_utc = str(json.dumps(datetime.datetime.utcnow().isoformat(sep=' ', timespec='seconds'), indent=4, sort_keys=True, default=str))
    dados = [momento, momento_utc, url, portal, resposta]
    return dados


def preenche_csv(arquivo_logs, dados):
    """
    Guarda as ultimas interaçõs do bot no arquivo csv previamente criado.
    As informações introduzidas são aquelas geradas pela função "cria_dados"
    """
    arq_log = Path(arquivo_logs)
    with open(arq_log, 'a', newline='', encoding='UTF8') as log_csv:
        escreve_log = csv.writer(log_csv)
        escreve_log.writerow(dados)


def preenche_tab_gs(planilha, dados):
    """
    Escrevendo na planilha
    """
    tabela = google_drive_creds.open(planilha.title)
    planilha = tabela.get_worksheet(index=0)
    planilha.append_row(values=dados)


def carregar_dados_site() -> csv.DictReader:
    """
    Abrindo a lista de portais da transparência e tratando
    informações que serão tratados como NaN para o pandas.
    """
    with open('dados/lista_portais.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return reader


def busca_disponibilidade_sites(sites):
    """
    Percorrendo a lista de sites para verificar
    a sua disponibilidade. Caso o código de status
    seja 200 (OK), então ela está disponível para acesso.
    """
    for index, row in sites:
        url, orgao = row['url'], row['orgao']

        for tentativa in range(TOTAL_TENTATIVAS):
            try:
                momento = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
                resposta = get(row['url'], timeout=30, headers=headers)
                dados = cria_dados(url=url, portal=orgao, resposta=resposta.status_code)
                preenche_csv(arquivo_logs=arq_log, dados=dados)
                if resposta.status_code == STATUS_SUCESSO:
                    print(f'{momento}; O site {url} funcionou corretamente.')
                    break
                else:
                    if tentativa == TOTAL_TENTATIVAS:
                        if not settings.debug:
                            preenche_tab_gs(planilha=planilha_google, dados=dados)
                        preenche_csv(arquivo_logs=arq_log, dados=dados)
                        print(f"""{momento}; url: {url}; orgão: {orgao}; resposta: {resposta.status_code}""")
                        if not settings.debug:
                            checar_timelines(mastodon_handler=mastodon_bot, url=url, orgao=orgao)

            except (exceptions.ConnectionError, exceptions.Timeout, exceptions.TooManyRedirects) as e:
                dados = cria_dados(url=url, portal=orgao, resposta=str(e))
                if not settings.debug:
                    preenche_tab_gs(planilha=planilha_google, dados=dados)
                preenche_csv(arquivo_logs=arq_log, dados=dados)
                print(f"""{momento}; url: {url}; orgão: {orgao}; resposta:{str(e)}""")
                if not settings.debug:
                    checar_timelines(mastodon_handler=mastodon_bot, url=url, orgao=orgao)
                break


if __name__ == '__main__':
    if not settings.debug:
        mastodon_bot = masto_auth()
        twitter_bot = twitter_auth()
        google_creds = google_api_auth()
        google_drive_creds = google_sshet()
        planilha_google = plan_gs(dia=DIA, mes=MES, ano=ANO)
    arq_log = plan_csv()
    sites = carregar_dados_site()
    while True:
        busca_disponibilidade_sites(sites)
        sleep(600)
