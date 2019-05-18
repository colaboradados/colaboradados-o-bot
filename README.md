# Colaborabot


<a href="https://twitter.com/colaboradados"> <img src="colaboradados_twitter_logo.png" width="200"></a>

O robô que monitora o acesso aos portais de transparência pública governamentais.
Siga [**@colabora_bot**](https://twitter.com/colabora_bot)

## Executando o bot

Crie o arquivo .env localmente no diretorio "credenciais" como mostra o arquivo `.env.example`.
Feito isso já é possível executar o bot utilizando
- `python main.py`

### Configução do Twitter (opcional)

Você deverá obter suas tokens para usar a API do Twitter: 

1. Crie sua conta normalmente, caso não a tenha. 
2. Em seguida solicite uma developer account [aqui](https://developer.twitter.com/en/apply/user). 

Hoje a requisição pode demorar dias (e há relatos de pessoas que nunca receberam). Seja o mais descritivo possível com relação ao seu projeto e fique atento aos e-mails, pois o Twitter poderá pedir informações adicionais. Também é por email que o Twitter avisará que sua requisição foi aceita. Caso isso aconteça: comemore (uhull!) e crie um app clicando [aqui](https://developer.twitter.com/en/apps). Desta forma você terá acesso as suas tokens que são: consumer_key, consumer_secret, access_token e access_token_secret.

### Configuração do Mastodonte (opcional)
//TODO

### Hora da instalação

Este código usa Python 3.7. Instale [aqui](https://www.python.org/downloads/).
Para as bibliotecas, instale todas de uma vez digitando `pip install -r requirements.txt`em seu terminal.

### Abrindo

1. Clone o repositório digitando `$ git clone https://github.com/colaboradados/colaboradadosobot` no Gitbash.
2. Vá até a pasta onde você clonou o repositório em seu computador. 
3. Pronto, agora é só editar seu bot!

### Colaborando com a bases de dados (e sendo uma pessoa muito legal)

O **Colaboradados** é uma iniciativa sem fins lucrativos e feita para comunidade e com a ajuda da mesma. Para ajudar com nossa base de dados você poderá resolver nossas issues ou editando diretamente nosso arquivo csv.

Fique atento ao fato de que nosso programa foi criado pensando no escopo nacional brasileiro, portanto seu código é - deverá ser - sempre em português, onde possível. Evite estrangeirismos e colabore para que nosso código seja estudado por todos aqueles interessados em transparência.

## Créditos

Este bot foi desenvolvido por [João Ernane](https://github.com/jovemadulto), [João Purger](https://github.com/JCPurger) e [Judite Cypreste](https://juditecypreste.github.io).

## The MIT License (MIT)

Copyright (c) 2019 Judite Cypreste

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
