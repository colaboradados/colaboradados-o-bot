from autenticadores import google_api_auth
from random import choice
import gspread


def google_sshet():
    """
    Função simples para retornar um objeto capaz de manipular as planilhas do Google Sheets.
    """
    session = google_api_auth()
    ggle_cred = gspread.Client(None, session)
    return ggle_cred
