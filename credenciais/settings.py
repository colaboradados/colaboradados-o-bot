import os
from dotenv import load_dotenv
from pathlib import Path


class Settings:

    print("carregando configuracoes...")

    env_path = Path('./credenciais') / '.env'
    load_dotenv(dotenv_path=env_path, override=True)

    # [Twitter API Keys]
    twitter_active = os.environ.get('TWITTER_ACTIVE') == True
    consumer_key = os.environ.get('CONSUMER_KEY')
    consumer_secret = os.environ.get('CONSUMER_SECRET')
    access_token = os.environ.get('ACCESS_TOKEN')
    access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

    # [Mastodon API Key]
    mastodon_active = os.environ.get('DONTE_ACTIVE') == True
    mastodon_key = os.environ.get('DONTE_USERCRED')

    # [Plataforms IDs]
    mastodon_profile_id = os.environ.get('ID_CONTA_MASTODON')
