from mastodon import Mastodon

class MastodonPublicador(object):

    def __init__(self, settings):
        try:
            #TODO: criar configuracao
            self.active = settings.mastodon_active
            self.mastodon_key = settings.mastodon_key

            self.mastodon_bot = self.__masto_auth()

        except Exception as e:
            raise e

    def criar_toot(self, publicacao, url):
        """
        Recupera os 10 últimos toots da conta do Mastodon.
        Caso a URL não esteja entre as últimas notificadas, é feita a postagem.
        Feature necessária para não floodar a timeline alheia caso um site fique offline por longos períodos de tempo.
        """

        if self.active == True:
            urls_postadas = []
            timeline = self.mastodon_bot.timeline_home(limit=10)
            for toot in timeline:
                urls_postadas.append(toot["content"])
            contem = any(url in toot
                        for toot in urls_postadas)
            if not contem:
                self.mastodon_bot.toot(publicacao)
        else:
            print(f'mastodonte desativado')
    
    def __masto_auth(self):
        mastodon = Mastodon(
            access_token=self.mastodon_key,
            api_base_url='https://botsin.space'
        )
        return mastodon