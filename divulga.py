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

# TODO renomear esta funcao para cria_frase
def lista_frases(url, orgao):
    com_orgao = [
        f"🤖 O portal com dados públicos {url} do órgão {orgao} parece não estar funcionando. Poderia me ajudar a checar?",
        f"🤖 Hum, parece que o site {url}, mantido pelo órgão {orgao}, está apresentando erro. Poderia dar uma olhadinha?",
        f"🤖 Poxa, tentei acessar {url} e não consegui. Este site é mantido pelo órgão {orgao}. Você pode confirmar isso?",
        f"🤖 Não consigo acessar {url}, e eu sei que ele é mantido pelo órgão {orgao}. Você pode me ajudar a verificar?",
        f"🤖 Sabe o portal {url}, mantido pelo orgão {orgao}? Ele parece estar fora do ar. Você pode confirmar?",
        f"🤖 Parece que {url} está apresentando probleminhas para ser acessado. Alguém pode avisar a(o) {orgao}?",
        f"🤖 Oi, parece que esse site {url} possui problemas de acesso. {orgao} está sabendo disso?",
        f"🤖 Portais da transparência são um direito ao acesso à informação {orgao}, mas parece que {url} está fora do ar.",
        f"🤖 Opa {orgao}, parece que o site {url} não está acessível como deveria. O que está acontecendo?",
        f"🤖 Tentei acessar o site {url} e não consegui. {orgao} está acontecendo algum problema com essa portal de transparência?",
    ]
    msg_orgao = choice(com_orgao)
    return msg_orgao

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
