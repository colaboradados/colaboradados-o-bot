from decouple import config

debug = config("DEBUG", default=False)

# [Twitter API Keys]
consumer_key = config("CONSUMER_KEY")
consumer_secret = config("CONSUMER_SECRET")
access_token = config("ACCESS_TOKEN")
access_token_secret = config("ACCESS_TOKEN_SECRET")

# [Mastodon API Key]
mastodon_key = config("DONTE_USERCRED")

# [Plataforms IDs]
mastodon_profile_id = config("ID_CONTA_MASTODON")

# [Google API Keys / IDs]
google_api_conf = "credenciais/colaborabot-gAPI.json"

# [Bracos do Colabora Bot]
import autenticadores
bracos = (autenticadores.Twitter, 
          autenticadores.Mastodon,
          autenticadores.GoogleSheet
)

