# Importando as libraries
import csv
import rows
import datetime
import requests
import http.client

from pathlib import Path
from time import sleep
import settings

from divulga import cria_frase, checar_timelines, google_sshet
from autenticadores import google_api_auth
from gspread.exceptions import APIError

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


def cria_dados(url, portal, resposta):
    """
    Captura as informações de hora e data da máquina, endereço da página e
    resposta recebida e as prepara dentro de uma lista para inserir na tabela.
    """
    formato_data = "%Y-%m-%d %H:%m:%S"
    momento = str(datetime.datetime.now().strftime(formato_data))
    momento_utc = datetime.datetime.utcnow().strftime(formato_data)
    dados = [momento, momento_utc, url, portal, resposta]
    return dados


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


if __name__ == "__main__":
    if not settings.debug:
        global bots_ativos
        bots_ativos = (bot() for bot in settings.bracos)

        #google_creds = google_api_auth()
        #google_drive
        #google_drive_creds = google_sshet()
        #planilha_google = plan_gs(dia=DIA, mes=MES, ano=ANO)
    sites = carregar_dados_site()
    while True:
        busca_disponibilidade_sites(sites)
