"""
Configuracoes globais para o projeto.

todas as variaveis globais devem ser definidas aqui bem como variaveis de ambiente
(nos arquivos .env) devem estar importadas e definidas neste arquivo
"""

import os
import logging

from pathlib import Path
from datetime import datetime

from decouple import config

# Id do repositorio no GitHub
# ? - Veja no dicionario de dados
APP_ID: int = 863490744


# Muda as configuracoes para se voce estiver em desenvolvimento do projeto
DEV_MODE = False

def if_not_dev(dev_false: any, dev_true: any = False) -> any:
    """Muda as configuracoes se DEV_MODE for True

    Args:
        dev_false: Valor a ser retornado se DEV_MODE for False
        dev_true: Valor a ser retornado se DEV_MODE for True

    Returns:
        O valor de dev_false se DEV_MODE for False, ou dev_true se DEV_MODE for True
    """
    return dev_true if DEV_MODE else dev_false


# Diretorio do projeto
BASE_DIR = Path(__file__).parent.parent.resolve()
TMP_DIR = BASE_DIR / "source/tmp"
TMP_DIR.mkdir(exist_ok = True)


# Arquivos na cloud
__ONEDRIVE = Path(os.path.expanduser("~/XP Investimentos"))
ONEDRIVE_GERAL = __ONEDRIVE / "Manchester - Mesa RV - General"
ONEDRIVE_BROKERS = __ONEDRIVE / "Manchester - Mesa RV - Brokers - Brokers"
ONEDRIVE_BACKOFFICE = __ONEDRIVE / "Manchester - Mesa RV - Backoffice - Backoffice"


# Database
DATABASE_DEV_URL = config("DATABASE_DEV_URL", default = None)
DATABASE_PROD_URL = config("DATABASE_PROD_URL", default = None)


# Logs
LOG_FOLDER = ONEDRIVE_BACKOFFICE / f"Base de dados/Logs/{datetime.now().strftime("%Y-%m-%d")}/{APP_ID}"
LOG_LEVEL = logging.INFO
LOG_VIA_EMAIL = if_not_dev(True)
LOG_VIA_ARQUIVO = True
LOG_VIA_DATABASE = if_not_dev(True)


# Emails
EMAIL_ENVIO = 'bianca.pamplona@manchesterinvest.com.br;flavia@manchesterinvest.com.br'
EMAIL_CC = 'marcos.neuhaus@manchesterinvest.com.br;henrique.toledo@manchesterinvest.com.br;gustavo.simao@manchesterinvest.com.br'
EMAIL_PC = 'ordens@manchesterinvest.com.br'
