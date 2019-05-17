from pathlib import Path

class LoggerCsv(object):

    def __init__(self, dia: int, mes: int, ano: int):
        self.dia = dia
        self.mes = mes
        self.ano = ano

        self.arq_log = __plan_csv()

    def preenche_csv(self, dados):
        """
        Guarda as ultimas interaçõs do bot no arquivo csv previamente criado.
        As informações introduzidas são aquelas geradas pela função "cria_dados"
        """
        arq_log = Path(arquivo_logs)
        with open(self.arq_log, 'a', newline='', encoding='UTF8') as log_csv:
            escreve_log = csv.writer(log_csv)
            escreve_log.writerow(dados)

    def __plan_csv(self):
        """
        Cria um arquivo local para guardar todas as interações do bot.
        """
        pasta_logs = Path(f'../../logs')
        arq_log = pasta_logs / f'colaborabot-log-{self.ano}-{self.mes}-{self.dia}.csv'
        if not pasta_logs.exists():
            pasta_logs.mkdir()
        arq_log.write_text(data='data_bsb;data_utc;url;orgao;cod_resposta\n', encoding='UTF8')
        return arq_log