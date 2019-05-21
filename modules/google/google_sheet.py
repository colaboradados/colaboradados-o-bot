import gspread
import json

from credenciais.settings import Settings
from pathlib import Path
from authlib.client import AssertionSession
from time import sleep

class GoogleSheet: 

	google_spread_client = None

	def __init__(self, dia: int, mes: int, ano: int):
		if not Settings.conexoes_desativadas:
			self.google_api_session = self.__google_api_auth()
			self.google_spread_client = self.__google_sshet() # antigo google_drive_creds
			self.planilha_google = self.__plan_gs(dia=dia, mes=mes, ano=ano)

			if self.google_spread_client is None:
				print("! conexão com google sheet não foi estabelecida")
		else:
			print('! Conexões desativadas, google sheet não será carregado.')

	def preenche_tab_gs(self, dados):
		"""
		Escrevendo na planilha
		"""
		if self.google_spread_client is not None:
			tabela = self.google_spread_client.open(self.planilha_google.title)
			planilha = tabela.get_worksheet(index=0)
			planilha.append_row(values=dados)

	def __plan_gs(self, dia, mes, ano):
		"""
		Cria planilha no Google Drive, envia por e-mail e preenche o cabeçalho (data e hora no fuso horário de Brasília,
		data e hora no UTC, url afetada, órgão responsável e código de resposta do acesso).
		A planilha criada possui as permissões de leitura para qualquer pessoa com o link, porém somente a conta da API do
		bot (que não é a mesma conta usada pela equipe) consegue alterar os dados contidos nela.

		Também é acessado uma planilha índice (docs.google.com/spreadsheets/d/1kIwjn2K0XKAOWZLVRBx9lOU5D4TTUanvmhzmdx7bh0w)
		e incluído a planilha de logs nela, na segunda tabela.
		"""

		if self.google_spread_client is not None:

			lista_planilhas = []
			todas_planilhas = self.google_spread_client.list_spreadsheet_files()

			for item in todas_planilhas:
				lista_planilhas.append(item['name'])

			if f'colaborabot-sites-offline-{dia:02d}{mes:02d}{ano:04d}' not in lista_planilhas:
				planilha = self.google_spread_client.create(f'colaborabot-sites-offline-{dia:02d}{mes:02d}{ano:04d}')  # Exemplo de nome final: colaborabot-sites-offline-27022019
				cabecalho = planilha.get_worksheet(index=0)
				cabecalho.insert_row(values=['data_bsb', 'data_utc', 'url', 'orgao', 'cod_resposta'])
				
				plan_indice = self.google_spread_client.open_by_key('1kIwjn2K0XKAOWZLVRBx9lOU5D4TTUanvmhzmdx7bh0w')
				tab_indice = plan_indice.get_worksheet(index=1)
				endereco = f'docs.google.com/spreadsheets/d/{planilha.id}/'
				data = '{:02d}/{:02d}/{:02d}'.format(DIA, MES, ANO) # 11/04/2019
				tab_indice.append_row(values=[data, endereco])

			else:
				planilha = self.google_spread_client.open(title=f'colaborabot-sites-offline-{dia:02d}{mes:02d}{ano:04d}')

			sleep(5)
			planilha.share(None, perm_type='anyone', role='reader')
			print(f'https://docs.google.com/spreadsheets/d/{planilha.id}\n')
			return planilha
		else:
			return None

	def __google_sshet(self):
		"""
		Função simples para retornar um objeto capaz de manipular as planilhas do Google Sheets.
		"""
		if self.google_api_session is not None:
			ggle_cred = gspread.Client(None, self.google_api_session)
			return ggle_cred
		else:
			return None

	def __google_api_auth(self, arqv_json='credenciais/colaborabot-gAPI.json', subject=None):
		file = Path(arqv_json)

		if file.is_file():
			with open(arqv_json, 'r') as f:
				conf = json.load(f)

			token_url = conf['token_uri']
			issuer = conf['client_email']
			key = conf['private_key']
			key_id = conf.get('private_key_id')

			header = {'alg': 'RS256'}
			scopes = [
				'https://spreadsheets.google.com/feeds',
				'https://www.googleapis.com/auth/drive'
			]

			if key_id:
				header['kid'] = key_id

			# Google puts scope in payload
			claims = {'scope': ' '.join(scopes)}
			return AssertionSession(
				grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
				token_url=token_url,
				issuer=issuer,
				audience=token_url,
				claims=claims,
				subject=subject,
				key=key,
				header=header,
			)
		else:
			print(f"arquivo não existe: '{arqv_json}'")
			print(f"conexao com googlesheets sera ignorada...")
			return None