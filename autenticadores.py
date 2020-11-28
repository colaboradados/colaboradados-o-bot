from abc import ABC, abstractmethod

from authlib.client import AssertionSession

import mastodon 
import settings
import tweepy
import json

from pathlib import Path
import datetime
import csv

from utils import cria_frase, cria_dados

"""
Braco
    inicializacao (autenticação)
    atualizar linha do tempo
    checa linha do tempo
"""

class BracoBase(ABC): # classe abstrata base
    def update(self, dados, checa_timeline=False):
        def enviar():
            mensagem = cria_frase(url=dados.url,
                    orgao=dados.orgao)
            self._update_real(mensagem)

        if checa_timeline:
            if not self._contem(dados.url):
                enviar()
        else:
            enviar()

    @abstractmethod
    def _update_real(self, mensagem):
        pass

    @abstractmethod
    def get_timeline(self, limite=10):
        pass

    @abstractmethod
    def _contem(self, url):
        pass


class Twitter(BracoBase):
    def __init__(self):
        consumer_key = settings.consumer_key
        consumer_secret = settings.consumer_secret
        access_token = settings.access_token
        access_token_secret = settings.access_token_secret

        # App no Twitter
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.bot = tweepy.API(auth)

    def _update_real(self, mensagem):
        self.bot.update_status(status=mensagem)

    def get_timeline(self, limite=10):
        pass
        # Ver http://docs.tweepy.org/en/latest/api.html#API.home_timeline
        # ou http://docs.tweepy.org/en/latest/code_snippet.html#pagination
        #return self.bot.home_timeline(count=limite)

    # escrever...
    def _contem(self, mensagem):
        return False


class Mastodon(BracoBase):
    def __init__(self):
        self.bot = mastodon.Mastodon(access_token=settings.mastodon_key,
                                     api_base_url="https://botsin.space")

    def _update_real(self, mensagem):
        self.bot.toot(mensagem)

    def get_timeline(self, limite=10):
        return self.bot.timeline_home(limit=limite)

    def _contem(self, url):
        timeline = self.get_timeline(limite=10)
        urls_postadas = [toot["content"] for toot in timeline]
        return any(url in toot for toot in urls_postadas)


class GoogleSheet(BracoBase):
    def load_conf(self):
        with open(settings.google_confs, "r") as f:
            conf = json.load(f)

        token_url = conf["token_uri"]
        issuer = conf["client_email"]
        key = conf["private_key"]
        key_id = conf.get("private_key_id")

        header = {"alg": "RS256"}
        scopes = ["https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive"]

        if key_id:
            header["kid"] = key_id

        # Google puts scope in payload
        claims = {"scope": " ".join(scopes)}
        return AssertionSession(
            grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
            token_url=token_url,
            issuer=issuer,
            audience=token_url,
            claims=claims,
            subject=subject,
            key=key,
            header=header,
        )

    def plan_gs(self):
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

    def __init__(self):
        self.conf = load_confs()
        self.indice = plan_gs()

    def update(self, mensagem, checa_timeline=False):
        pass
        ##colaborabot.plan_gs...

    def get_timeline(self, limite=10):
        pass


class Telegram(BracoBase):
    pass

class CSV(BracoBase):
    def __init__(self):
        pasta_logs = Path("logs")
        if not pasta_logs.exists():
            pasta_logs.mkdir()

        DIA = datetime.datetime.now().day
        MES = datetime.datetime.now().month
        ANO = datetime.datetime.now().year

        self.arq_log = pasta_logs / f"colaborabot-log-{ANO}-{MES}-{DIA}.csv"
        cabecalho = ["data_bsb", "data_utc", "url", "orgao", "cod_resposta"]
        with open(self.arq_log, "w") as csvfile:
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            csv_writer.writerow(cabecalho)

    def _update_real(self, mensagem):
        with open(self.arq_log, "a") as csvfile:
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            csv_writer.writerow(mensagem)

    def update(self, dados, checa_timeline=False):
        mensagem = cria_dados(dados.url, dados.orgao, dados.resposta)
        self._update_real(mensagem)

    def get_timeline(self, limite=10):
        pass

    def _contem(self, url):
        pass

def google_api_auth(arqv_json="credenciais/colaborabot-gAPI.json", subject=None):
    with open(arqv_json, "r") as f:
        conf = json.load(f)

    token_url = conf["token_uri"]
    issuer = conf["client_email"]
    key = conf["private_key"]
    key_id = conf.get("private_key_id")

    header = {"alg": "RS256"}
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    if key_id:
        header["kid"] = key_id

    # Google puts scope in payload
    claims = {"scope": " ".join(scopes)}
    return AssertionSession(
        grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
        token_url=token_url,
        issuer=issuer,
        audience=token_url,
        claims=claims,
        subject=subject,
        key=key,
        header=header,
    )

