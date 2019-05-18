# from sys import path
# path.insert(0,'/modules')
from time import sleep
from modules.colaborabot import Colaborabot
from credenciais.settings import Settings

if __name__ == '__main__':
    
    tempo_busca = 600
    
    #criando bot
    colaborabot = Colaborabot(Settings)

    # executa analise a cada 600ms
    while True:
        print("iniciando buscas...")
        colaborabot.busca_disponibilidade_sites()
        print(f"buscas finalizadas, iniciando novamente em {tempo_busca}...")
        sleep(tempo_busca)