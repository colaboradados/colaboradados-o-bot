import tweepy
from autenticadores import google_api_auth
from random import choice
import gspread

# TODO remover (?)
def google_sshet():
    """
    Função simples para retornar um objeto capaz de manipular as planilhas do Google Sheets.
    """
    session = google_api_auth()
    ggle_cred = gspread.Client(None, session)
    return ggle_cred


# TODO remover
def checar_timelines(twitter_hander, mastodon_handler, url, orgao):
    """
    Recupera os 10 últimos toots/tweets da conta do Mastodon/Twitter.
    Caso a URL não esteja entre as últimas notificadas, é feita a postagem.
    Feature necessária para não floodar a timeline alheia caso um site fique offline por longos períodos de tempo.
    """

    mastodon_bot = mastodon_handler
    twitter_bot = twitter_hander
    
    timeline = mastodon_bot.timeline_home(limit=10)
    urls_postadas = [toot["content"] for toot in timeline]
    contem = any(url in toot for toot in urls_postadas)
    if not contem:
        mastodon_bot.toot(lista_frases(url=url, orgao=orgao))
        try:
            twitter_bot.update_status(status=lista_frases(url=url, orgao=orgao))
        except tweepy.TweepError as error:
            if error.api_code == 187:
                print('duplicate message')
            else:
                raise error
