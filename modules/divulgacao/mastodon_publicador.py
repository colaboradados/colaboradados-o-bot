from mastodon import Mastodon

class MastodonPublicador:

    mastodon_key = None
    mastodon_bot = None

    def __init__(self, settings):
        if not settings.conexoes_desativadas:
            self.active = settings.mastodon_active
            if self.active:
                self.mastodon_key = settings.mastodon_key
                self.mastodon_bot = self.__masto_auth()
            else:
                print('! mastodonte desativado.')
        else:
            print('! Conexões desativadas, mastodonte não será carregado.')

    def criar_toot(self, publicacao, url):
        """
        Recupera os 10 últimos toots da conta do Mastodon.
        Caso a URL não esteja entre as últimas notificadas, é feita a postagem.
        Feature necessária para não floodar a timeline alheia caso um site fique offline por longos períodos de tempo.
        """

        if self.mastodon_bot is not None:
            urls_postadas = []
            timeline = self.mastodon_bot.timeline_home(limit=10)
            for toot in timeline:
                urls_postadas.append(toot["content"])
            contem = any(url in toot
                        for toot in urls_postadas)
            if not contem:
                self.mastodon_bot.toot(publicacao)
                print("toot postado!")
    
    def __masto_auth(self):
        if self.mastodon_key is not None:
            mastodon = Mastodon(
                access_token=self.mastodon_key,
                api_base_url='https://botsin.space'
            )
            return mastodon
        return None