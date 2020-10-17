from abc import ABC, abstractmethod

from authlib.client import AssertionSession
from mastodon import Mastodon
import settings
import tweepy
import json


"""
Braco
    inicializacao (autenticação)
    atualizar linha do tempo
    checa linha do tempo
"""

class BracoBase(ABC): # classe abstrata base
    @abstractmethod
    def update(self, mensagem, checa_timeline=False):
        pass

    @abstractmethod
    def get_timeline(self, limite=10):
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

    def update(self, mensagem, checa_timeline=False):
        self.bot.update_status(status=mensagem)

    def get_timeline(self, limite=10):
        pass


class Mastodon(BracoBase):
    def __init__(self):
        self.bot = Mastodon(access_token=settings.mastodon_key, api_base_url="https://botsin.space")

    def update(self, mensagem, checa_timeline=False):
        if checa_timeline and self.contem(mensagem):
            self.bot.toot(mensagem)
        else:
            self.bot.toot(mensagem)

    def get_timeline(self, limite=10):
        return self.bot.timeline_home(limit=10)

    def contem(mensagem):
        timeline = self.bot.get_timeline_home(limit=10)
        urls_postadas = [toot["content"] for toot in timeline]
        return any(url in toot for toot in urls_postadas)


class GoogleSheet(BracoBase):
    pass


class Telegram(BracoBase):
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

