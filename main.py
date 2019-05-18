
from time import sleep
from src.colaborabot import Colaborabot
from credenciais.settings import Settings



if __name__ == '__main__':
    #criando bot
    colaborabot = Colaborabot(Settings)

    # executa analise a cada 600ms
    while True:
        colaborabot.busca_disponibilidade_sites()
        sleep(600)