
import tweepy

class TwitterPublicador:
    
    def __init__(self, settings):
        try:
            self.active = settings.twitter_active
            self.consumer_key = settings.consumer_key
            self.consumer_secret = settings.consumer_secret
            self.access_token = settings.access_token
            self.access_token_secret = settings.access_token_secret
            
            self.twitter_bot = self.__twitter_auth()

        except Exception as e:
            raise e

    def criar_tweet(self, publicacao):
        """
        Criando o tweet com o status do site recém acessado
        """
        if self.active == True:
            self.twitter_bot.update_status(publicacao)
            print("tweet postado!")
        else:
            print(f'twitter desativado.')

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