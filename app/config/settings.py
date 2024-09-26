"""
Arquivo de configuracoes para o projeto, todas as variaveis globais devem ser definidas aqui.
"""

import os
from pathlib import Path
from datetime import datetime

# Id do repositório no GitHub, veja nas referencias dicionario de dados
APP_ID: int = None


# Muda as configuracoes para se voce estiver em desenvolvimento do projeto
DEV_MODE = True

def if_not_dev(if_not_dev: any, if_dev: any = False) -> any:
    return if_dev if DEV_MODE else if_not_dev


# Diretório do projeto.
APP_DIRECTORY = Path(__file__).resolve().parent.parent


# Diretório do usuário.
USER_DIRECTORY = Path(os.path.expanduser("~"))


# Serviços de armazenamento online.
DROPBOX = USER_DIRECTORY / "MESA FÊNIX Dropbox/Mesa RV Manchester"
ONEDRIVE_GERAL = USER_DIRECTORY / "XP Investimentos/Manchester - Mesa RV - General"
ONEDRIVE_BROKERS = USER_DIRECTORY / "XP Investimentos/Manchester - Mesa RV - Brokers - Brokers"
ONEDRIVE_BACKOFFICE = USER_DIRECTORY / "XP Investimentos/Manchester - Mesa RV - Backoffice - Backoffice"


# Logs.
LOG_FOLDER = ONEDRIVE_BACKOFFICE / f"Base de dados/Logs/{datetime.now().strftime("%Y-%m-%d")}/{APP_ID}"
LOG_VIA_EMAIL = if_not_dev(True)
LOG_VIA_ARQUIVO = True
LOG_VIA_DATABASE = if_not_dev(True)
