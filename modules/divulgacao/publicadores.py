from random import choice

from modules.divulgacao.twitter_publicador import TwitterPublicador
from modules.divulgacao.mastodon_publicador import MastodonPublicador

class Publicadores:
    """
    publicadores é a classe responsavel por publicar em todas as redes de divulgacao. Ex: twitter, mastodon, etc.
    """
    
    def __init__(self):
        print("iniciando twitter...")
        self.twitter_publicador = TwitterPublicador()

        print("iniciando mastodon...")
        self.mastodon_publicador = MastodonPublicador()
    
    def criar_publicacao(self, url, orgao):
        publicacao = self.__lista_frases(url=url, orgao=orgao)

        print(f'Publicando: {publicacao}')

        self.twitter_publicador.criar_tweet(publicacao)
        self.mastodon_publicador.criar_toot(publicacao, url)


    def __lista_frases(self, url, orgao):
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
            f"🤖 Tentei acessar o site {url} e não consegui. {orgao} está acontecendo algum problema com essa portal de transparência?"
        ]
        msg_orgao = choice(com_orgao)
        return msg_orgao
