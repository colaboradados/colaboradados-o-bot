from time import sleep
from modules.colaborabot import Colaborabot

if __name__ == '__main__':
    
    tempo_busca = 600
    
    #criando bot
    colaborabot = Colaborabot()

    # executa analise a cada 600ms
    while True:
        print("iniciando buscas...")
        colaborabot.busca_disponibilidade_sites()
        print(f"buscas finalizadas, iniciando novamente em {tempo_busca} segundos...")
        sleep(tempo_busca)