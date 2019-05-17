
from time import sleep
from src.colaborabot import Colaborabot




if __name__ == '__main__':
    #criando bot
    colaborabot = Colaborabot()

    # executa analise a cada 600ms
    while True:
        colaborabot.busca_disponibilidade_sites()
        sleep(600)