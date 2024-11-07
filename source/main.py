"""Módulo principal que executa as funções main de cada módulo dentro de source"""

import os
from outlook import Outlook
from etl import extrai_dados
from powerpoint import cria_pdf
from imagem import transforma_em_png
from settings import BASE_DIR, EMAIL_CC, EMAIL_ENVIO, EMAIL_PC

def main() -> None:
    """Função que executa todas as funções principais dos outros módulos."""

    outlook = Outlook(EMAIL_PC)
    template_fechamento_mercado_dev = BASE_DIR / "source/assets/template.pptm"
    template_fechamento_mercado_prd = BASE_DIR / "source/tmp/publicacao_fechamento_mercado.pptm"
    publicacao_fechamento_mercado_png = BASE_DIR / "source/tmp/publicacao_fechamento_mercado.png"

    # Extrai os dados sobre os ativos do site yahoo finance
    valores_dos_ativos, acoes_em_alta_baixa = extrai_dados()

    # Cria o PDF do Fechamento de Mercado
    cria_pdf(
        valores_dos_ativos,
        acoes_em_alta_baixa,
        template_fechamento_mercado_dev,
        template_fechamento_mercado_prd
    )

    # Transforma o arquivo de PPT para PNG e salva o arquivo na pasta TMP (temporária)
    transforma_em_png(template_fechamento_mercado_prd, publicacao_fechamento_mercado_png)

    outlook.enviar_email(
        para = EMAIL_ENVIO,
        copia_carbono = EMAIL_CC,
        assunto = "Envio do Fechamento do Mercado de hoje",
        corpo = (
            (BASE_DIR / "source/assets/tamplate_email.html")
            .read_text("utf-8")
        ),
        anexos = BASE_DIR / "source/tmp/publicacao_fechamento_mercado.png"
    )

    for file in (BASE_DIR / "source/tmp").iterdir():
        os.remove(file)

if __name__ == '__main__':
    main()
