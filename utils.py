from random import choice
import datetime

def cria_frase(url, orgao):
    com_orgao = [
        f"🤖 O portal com dados públicos {url} do órgão {orgao} parece não estar funcionando. Poderia me ajudar a checar?",
        f"🤖 Hum, parece que o site {url}, mantido pelo órgão {orgao}, está apresentando erro. Poderia dar uma olhadinha?",
        f"🤖 Poxa, tentei acessar {url} e não consegui. Este site é mantido pelo órgão {orgao}. Você pode confirmar isso?",
        f"🤖 Não consigo acessar {url}, e eu sei que ele é mantido pelo órgão {orgao}. Você pode me ajudar a verificar?",
        f"🤖 Sabe o portal {url}, mantido pelo orgão {orgao}? Ele parece estar fora do ar. Você pode confirmar?",
        f"🤖 Parece que {url} está apresentando probleminhas para ser acessado. Alguém pode avisar a(o) {orgao}?",
        f"🤖 Oi, parece que esse site {url} possui problemas de acesso. {orgao} está sabendo disso?",
        f"🤖 Portais da transparência são um direito ao acesso à informação {orgao}, mas parece que {url} está fora do ar.",
        f"🤖 Opa {orgao}, parece que o site {url} não está acessível como deveria. O que está acontecendo?",
        f"🤖 Tentei acessar o site {url} e não consegui. {orgao} está acontecendo algum problema com essa portal de transparência?",
    ]
    msg_orgao = choice(com_orgao)
    return msg_orgao

def cria_dados(url, portal, resposta):
    """
    Captura as informações de hora e data da máquina, endereço da página e
    resposta recebida e as prepara dentro de uma lista para inserir na tabela.
    """
    formato_data = "%Y-%m-%d %H:%m:%S"
    momento = str(datetime.datetime.now().strftime(formato_data))
    momento_utc = datetime.datetime.utcnow().strftime(formato_data)
    dados = [momento, momento_utc, url, portal, resposta]
    return dados

