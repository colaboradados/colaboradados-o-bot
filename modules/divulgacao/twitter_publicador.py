
import tweepy

class TwitterPublicador:
    
    twitter_bot = None

    def __init__(self, settings):
        if not settings.conexoes_desativadas:
            self.active = settings.twitter_active
            self.consumer_key = settings.consumer_key
            self.consumer_secret = settings.consumer_secret
            self.access_token = settings.access_token
            self.access_token_secret = settings.access_token_secret
            
            self.twitter_bot = self.__twitter_auth()

            if self.active == False:
                print('! twitter desativado.')
        else:
            print('! Conexões desativadas, twitter não será carregado.')

    def criar_tweet(self, publicacao):
        """
        Criando o tweet com o status do site recém acessado
        """
        if self.twitter_bot is not None:
            self.twitter_bot.update_status(publicacao)
            print("tweet postado!")

    def __twitter_auth(self):
        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        access_token = self.access_token
        access_token_secret = self.access_token_secret

        # App no Twitter

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        bot = tweepy.API(auth)
        return bot