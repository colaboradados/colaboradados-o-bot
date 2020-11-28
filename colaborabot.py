# Importando as libraries
import csv
import rows
import datetime
import requests
import http.client

from pathlib import Path
from time import sleep
import settings

from collections import namedtuple

from divulga import checar_timelines, google_sshet
from autenticadores import google_api_auth
from gspread.exceptions import APIError

from utils import cria_frase

http.client._MAXHEADERS = 1000

# Parametros de acesso das urls

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/39.0.2171.95 Safari/537.36"
    )
}

TOTAL_TENTATIVAS = 5
STATUS_SUCESSO = 200

# Guardando informações de hora e data da máquina

DIA = datetime.datetime.now().day
MES = datetime.datetime.now().month
ANO = datetime.datetime.now().year

data = "{:02d}/{:02d}/{:02d}".format(DIA, MES, ANO)  # 11/04/2019

def plan_gs(dia, mes, ano):
    """
    Cria planilha no Google Drive, envia por e-mail e preenche o cabeçalho
    (data e hora no fuso horário de Brasília, data e hora no UTC, url afetada,
    órgão responsável e código de resposta do acesso).
    A planilha criada possui as permissões de leitura para qualquer pessoa com
    o link, porém somente a conta da API do bot (que não é a mesma conta usada
    pela equipe) consegue alterar os dados contidos nela.

    Também é acessado uma planilha índice
    (docs.google.com/spreadsheets/d/1kIwjn2K0XKAOWZLVRBx9lOU5D4TTUanvmhzmdx7bh0w)
    e incluído a planilha de logs nela, na segunda tabela.
    """

    todas_planilhas = google_drive_creds.list_spreadsheet_files()
    lista_planilhas = [item["name"] for item in todas_planilhas]

    offline_titulo = f"colaborabot-sites-offline-{dia:02d}{mes:02d}{ano:04d}"

    if offline_titulo not in lista_planilhas:
        # Exemplo de nome final: colaborabot-sites-offline-27022019
        planilha = google_drive_creds.create(offline_titulo)
        cabecalho = planilha.get_worksheet(index=0)
        cabecalho.insert_row(values=["data_bsb", "data_utc", "url", "orgao", "cod_resposta"])

        plan_indice = google_drive_creds.open_by_key("1kIwjn2K0XKAOWZLVRBx9lOU5D4TTUanvmhzmdx7bh0w")
        tab_indice = plan_indice.get_worksheet(index=1)
        endereco = f"docs.google.com/spreadsheets/d/{planilha.id}/"
        tab_indice.append_row(values=[data, endereco])

    else:
        planilha = google_drive_creds.open(title=offline_titulo)

    sleep(5)
    planilha.share(None, perm_type="anyone", role="reader")
    print(f"https://docs.google.com/spreadsheets/d/{planilha.id}\n")
    return planilha


def preenche_csv(resultados):
    """
    Armazena os resultados da última execução do bot em um arquivo CSV.
    """
    pasta_logs = Path("logs")
    if not pasta_logs.exists():
        pasta_logs.mkdir()

    arq_log = pasta_logs / f"colaborabot-log-{ANO}-{MES}-{DIA}.csv"

    cabecalho = ["data_bsb", "data_utc", "url", "orgao", "cod_resposta"]
    with open(arq_log, "w") as csvfile:
        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        csv_writer.writerow(cabecalho)
        csv_writer.writerows(resultados)


def preenche_tab_gs(planilha, dados):
    """
    Escrevendo na planilha
    """
    try:
        tabela = google_drive_creds.open(planilha.title)
        planilha = tabela.get_worksheet(index=0)
        planilha.append_row(values=dados)
        return True
    except APIError:
        return False


def carregar_dados_site():
    """
    Abrindo a lista de portais da transparência e tratando
    informações que serão tratados como NaN para o pandas.
    """
    return rows.import_from_csv("dados/lista_portais.csv")


def busca_disponibilidade_sites(sites):
    """
    Percorrendo a lista de sites para verificar
    a sua disponibilidade. Caso o código de status
    seja 200 (OK), então ela está disponível para acesso.
    """
    resultados = []
    last_exception = ""

    for row in sites:
        url, orgao = row.url, row.orgao
        for tentativa in range(TOTAL_TENTATIVAS):
            try:
                if last_exception == "SSLError":
                    resposta = requests.get(url, headers=headers, timeout=60, verify=False)
                    status_code = resposta.status_code
                else:
                    resposta = requests.get(url, headers=headers, timeout=60)
                    status_code = resposta.status_code
                print("{} - {} - {}".format(orgao, url, status_code))
                last_exception = ""

                if status_code != STATUS_SUCESSO:
                    dados = cria_dados(url=url, portal=orgao, resposta=status_code)
                    if not settings.debug:
                        planilha_preenchida = False
                        while not planilha_preenchida:
                            planilha_preenchida = preenche_tab_gs(planilha=planilha_google, dados=dados)
                        resultados.append(dados)
                        
                        global bots_ativos
                        for bot in bots_ativos:
                            bot.update(checa_timeline=True, mensagem=cria_frase(url=url, orgao=orgao))

            except requests.exceptions.RequestException as e:
                print("Tentativa {}:".format(tentativa + 1))
                print(e)
                if e.__class__.__name__ == "SSLError":
                    last_exception = e.__class__.__name__
                    with open("bases-sem-certificados.txt", "a", encoding="utf-8") as no_certification:
                        no_certification.write("{} - {} - {}\n".format(orgao, url, e))
                    continue
                elif tentativa < TOTAL_TENTATIVAS - 1:
                    continue
                else:
                    with open("bases-com-excecoes.txt", "a", encoding="utf-8") as excecoes:
                        excecoes.write("{} - {} - {}\n".format(orgao, url, e))

            break

    preenche_csv(resultados)

def filtra_inativos(sites):
    """
    Percorrendo a lista de sites para verificar
    a sua disponibilidade. Caso o código de status
    seja 200 (OK), então ela está disponível para acesso.
    Se não estiver disponível pra acessar, retorna o site.
    """
    
    last_exception = None
    
    for row in sites:
        url, orgao = row.url, row.orgao
        for tentativa in range(TOTAL_TENTATIVAS):
            try:
                resposta = requests.get(url,
                                        headers=headers,
                                        timeout=60,
                                        verify=not(last_exception == "SSLError"))
                status_code = resposta.status_code
                # TODO ver esse print
                print("{} - {} - {}".format(orgao, url, status_code))
                last_exception = ""

                if status_code != STATUS_SUCESSO:
                    Site = namedtuple("Site", "orgao url resposta")
                    site = Site(row.orgao, row.url, status_code)
                    yield site

                break
            except requests.exceptions.RequestException as e:
                # TODO rever isso
                print("Tentativa {}:".format(tentativa + 1))
                print(e)
                if e.__class__.__name__ == "SSLError":
                    last_exception = e.__class__.__name__
                    with open("bases-sem-certificados.txt", "a", encoding="utf-8") as no_certification:
                        no_certification.write("{} - {} - {}\n".format(orgao, url, e))
                    continue
                elif tentativa < TOTAL_TENTATIVAS - 1:
                    continue
                else: # TODO rever esses excecoes e colocar alguns como sites inativos
                    with open("bases-com-excecoes.txt", "a", encoding="utf-8") as excecoes:
                        excecoes.write("{} - {} - {}\n".format(orgao, url, e))
                    break

if __name__ == "__main__":
    # se os bracos foram habilitados no settings,
    # talvez nao seja mais necessario esse if debug...
    if not settings.debug:
        pass

    sites = carregar_dados_site()
    bots_ativos = tuple(bot() for bot in settings.bracos)
    while True:
        for site in filtra_inativos(sites):
            for bot in bots_ativos:
                bot.update(checa_timeline=True, dados=site)

