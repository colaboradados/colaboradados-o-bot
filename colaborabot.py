# Importando as libraries

import numpy as np
import pandas as pd
import datetime
import json
import csv

from pathlib import Path
from requests import get, exceptions
from src.google.google_sheet import GoogleSheet
from src.divulgacao.publicadores import Publicadores



class Colaborabot(object):

    # Parametros de acesso das urls

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    DIA = datetime.datetime.now().day
    MES = datetime.datetime.now().month
    ANO = datetime.datetime.now().year

    TOTAL_TENTATIVAS = 10
    STATUS_SUCESSO = 200

    def __init(self):
        try:
            self.publicadores = Publicadores()
            self.google_sheet = GoogleSheet(DIA, MES, ANO)
        except Exception as e:
            raise e

    def busca_disponibilidade_sites(self):
        """
        Percorrendo a lista de sites para verificar
        a sua disponibilidade. Caso o código de status
        seja 200 (OK), então ela está disponível para acesso.

        Caso os sites ainda não tiverem sido carregados, eles serão.
        """
        
        self.__carregar_dados_site()

        for index, row in self.sites.iterrows():
            url, orgao = row['url'], row['orgao']

            for tentativa in range(TOTAL_TENTATIVAS):
                try:
                    momento = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
                    resposta = get(row['url'], timeout=30, headers=headers)
                    dados = self.__cria_dados(url=url, portal=orgao, resposta=resposta.status_code)
                    self.__preenche_csv(arquivo_logs=arq_log, dados=dados)
                    if resposta.status_code == STATUS_SUCESSO:
                        print(f'{momento}; O site {url} funcionou corretamente.')
                        break
                    else:
                        if tentativa == TOTAL_TENTATIVAS:
                            self.google_sheet.preenche_tab_gs(dados=dados)
                            self.__preenche_csv(arquivo_logs=arq_log, dados=dados)
                            print(f"""{momento}; url: {url}; orgão: {orgao}; resposta: {resposta.status_code}""")
                            self.publicadores.criar_publicacao(url=url, orgao=orgao)

                except (exceptions.ConnectionError, exceptions.Timeout, exceptions.TooManyRedirects) as e:
                    dados = self.__cria_dados(url=url, portal=orgao, resposta=str(e))
                    self.google_sheet.preenche_tab_gs(dados=dados)
                    self.__preenche_csv(arquivo_logs=arq_log, dados=dados)
                    print(f"""{momento}; url: {url}; orgão: {orgao}; resposta:{str(e)}""")
                    self.publicadores.criar_publicacao(url=url, orgao=orgao)
                    break
    
    def __cria_dados(self, url, portal, resposta):
        """
        Captura as informações de hora e data da máquina, endereço da página e
        resposta recebida e as prepara dentro de uma lista para inserir na tabela.
        """

        momento = str(json.dumps(datetime.datetime.now().isoformat(sep=' ', timespec='seconds'), indent=4, sort_keys=True, default=str))
        momento_utc = str(json.dumps(datetime.datetime.utcnow().isoformat(sep=' ', timespec='seconds'), indent=4, sort_keys=True, default=str))
        dados = [momento, momento_utc, url, portal, resposta]
        return dados

    def __preenche_csv(self, arquivo_logs, dados):
        """
        Guarda as ultimas interaçõs do bot no arquivo csv previamente criado.
        As informações introduzidas são aquelas geradas pela função "cria_dados"
        """
        arq_log = Path(arquivo_logs)
        with open(arq_log, 'a', newline='', encoding='UTF8') as log_csv:
            escreve_log = csv.writer(log_csv)
            escreve_log.writerow(dados)

    def __carregar_dados_site(self):
        """
        Abrindo a lista de portais da transparência e tratando
        informações que serão tratados como NaN para o pandas.
        sites sao carregados na instancia deste objeto
        """
        if self.sites is None:
            df = pd.read_csv(
                'lista_portais.csv',
                header=None,
                names=['url', 'arroba', 'orgao'],
                sep=';'
            )
            df = df.replace(np.nan, '', regex=True)
            self.sites = df
