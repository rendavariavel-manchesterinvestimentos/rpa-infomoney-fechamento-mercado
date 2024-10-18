"""Extrai dados dos ativos principais e dos ativos em alta e baixapara o fechamento
do mercado direto do site Yahoo Finance e formata deixando em formato de Dicionário"""

import time
import io
import logging
import pandas as pd
import numpy as np
import pandera as pa

from pandera import Column, DataFrameSchema, Check

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Configuração do logger com envio de email
logger = logging

def extrai_dados() -> tuple[dict, dict]:
    """Função principal que retorna os dados extraídos do site Yahoo Finance em formato de dicionário.

    ### Returns:
    - valores_dos_ativos (dict): Dicionário com dados dos ativos principais
    - acoes_em_alta_baixa (dict): Dicionário com dados dos ativos em alta e baixa
    """

    # Extract
    variacao_ativos_principais, variacao_altas_baixas = obter_variacao_ativos()

    # Transform
    valores_dos_ativos = formata_df_ativos_principais(variacao_ativos_principais)
    acoes_em_alta_baixa = formata_df_altas_baixas_concat(variacao_altas_baixas)

    # Load
    return valores_dos_ativos, acoes_em_alta_baixa

def obter_variacao_ativos() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Obtem os dados de Variação dos ativos principais e dos ativos em alta e baixa

    ### Returns:
    - variacao_ativos_principais (pd.DataFrame): DataFrame com dados de Variação dos ativos principais
    - variacao_altas_baixas (pd.DataFrame): DataFrame com dados de Variação dos ativos em alta e baixa
    """

    options = Options()
    options.add_argument("--log-level=3")

    browser = webdriver.Chrome(options = options)
    browser.get("https://login.yahoo.com/")

    WebDriverWait(browser, 60).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div[2]/form/div[1]/div[3]/input"))
    ).send_keys("mesarv01teams@manchesterinvest.com.br")

    browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div[2]/form/div[2]/input").click()

    time.sleep(1)
    WebDriverWait(browser, 60).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div[2]/form/div[2]/input"))
    ).send_keys("violino-MATADOR-galaxia")

    time.sleep(1)
    browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div[2]/form/div[3]/div[1]/button").click()


    # Extrai os dados do meu portfólio
    browser.get("https://br.financas.yahoo.com/portfolio/p_1/view/v1")
    time.sleep(1)

    df_ativos_principais = pd.read_html(io.StringIO(browser.page_source))[0]

    # Extrai as maiores variações
    browser.get("https://br.financas.yahoo.com/noticias/acoes-em-alta/")
    time.sleep(1)

    df_maiores_variacoes = pd.read_html(io.StringIO(browser.page_source), decimal = ",")[0]

    #Extrai as menores variações
    browser.get("https://br.financas.yahoo.com/noticias/acoes-em-baixa/")
    time.sleep(1)

    df_menores_variacoes = pd.read_html(io.StringIO(browser.page_source), decimal = ",")[0]

    df_altas_baixas_concat = pd.concat([df_maiores_variacoes, df_menores_variacoes], ignore_index=True)

    browser.quit()

    return df_ativos_principais, df_altas_baixas_concat

def formata_df_ativos_principais(df_ativos_principais: pd.DataFrame) -> dict:
    """Formata o dataframe dos ativos principais e transforma em dicionário.

    ### Argumentos:
    - df_ativos_principais (pd.DataFrame): DataFrame com dados dos ativos principais

    ### Returns:
    - valores_dos_ativos (dict): Dicionário com os dados dos ativos principais
    """

    df_ativos_principais.rename(
        columns={
            'Símbolo': 'Ticker',
            'Último Preço': 'Valor',
            '% de var.': 'Variação',
        },
        inplace=True
    )
    # Ativos
    df_ativos_principais = df_ativos_principais.reindex(
        columns = ['Ticker', 'Valor', 'Variação'],
    )

    df_ativos_principais["Variação"] = df_ativos_principais["Variação"].apply(convert_to_float)

    # Formata a coluna Valor e tranforma em float
    df_ativos_principais["Valor"] = df_ativos_principais["Valor"].apply(convert_to_float)
    df_ativos_principais.loc[df_ativos_principais["Ticker"] == "BRL=X", "Valor"] /= 10000
    df_ativos_principais["Valor"] = df_ativos_principais["Valor"].round(2)


    # Verificar antes de converter para dicionario
    schema = DataFrameSchema(
        columns = {
            "Ticker": Column(
                pa.String,
                nullable = False,
                checks = Check.isin(["^GSPC", "^IXIC", "EURBRL=X", "BRL=X", "^BVSP"])
            ),
            "Valor": Column(pa.Float, nullable = False),
            "Variação": Column(pa.Float, nullable = False)
        }
    )

    try:
        schema.validate(df_ativos_principais)
    except pa.errors.SchemaError as e:
        raise e


    # Cria dicionário df_ativos_principais
    ativos = df_ativos_principais.to_dict(orient = "records")

    valores_dos_ativos = {
        "ativos": ativos,
    }

    return valores_dos_ativos

def formata_df_altas_baixas_concat(df_altas_baixas_concat: pd.DataFrame) -> dict:
    """Formata o dataframe dos ativos em alta e em baixa e transforma em dicionário.

    ### Argumentos:
    - df_altas_baixas_concat (pd.DataFrame): DataFrame com dados dos ativos principais

    ### Returns:
    - acoes_em_alta_baixa (dict): Dicionário com os dados dos ativos principais
    """

    #Renomeia o dataframe
    df_altas_baixas_concat.rename(
        columns={
            'Símbolo': 'Ticker',
            'Preço (em um dia)': 'Valor',
            '% de variação': 'Variação',
        },
        inplace = True
    )

    # Maiores e Menores Variações
    df_altas_baixas_concat = df_altas_baixas_concat.reindex(
        columns = ['Ticker', 'Valor', 'Variação'],
    )

    regex_ticker = r"([A-Z]{4}[\d]{2}|[A-Z]{4}[\d]{1}).SA"

    # Filtra ps tickers corretos
    df_altas_baixas_concat = df_altas_baixas_concat[df_altas_baixas_concat["Ticker"].str.contains(regex_ticker, regex = True)]

    # Obtem os grupos
    df_altas_baixas_concat["Ticker"] = df_altas_baixas_concat["Ticker"].str.extract(regex_ticker)


    # Transforma em float
    df_altas_baixas_concat["Variação"] = df_altas_baixas_concat["Variação"].apply(convert_to_float)

    df_altas_baixas_concat = df_altas_baixas_concat.astype(
        dtype = {
            "Ticker": str,
            "Valor": float,
            "Variação": float,
        }
    )

    # Verificar antes de converter para dicionario
    schema = DataFrameSchema(
            columns = {
                "Ticker": Column(
                        pa.String, checks=[
                        Check.str_length(
                            5, 6, error="Os valores na coluna 'Ticker' devem ter entre 5 e 6 caracteres."
                        )
                    ]
                ),
                "Valor": Column(pa.Float, nullable=False),
                "Variação": Column(pa.Float, nullable=False)
            }
    )

    try:
        schema.validate(df_altas_baixas_concat)

    except pa.errors.SchemaError as exception:
        raise exception

    # Cria dicionário df cotação concatenado
    maiores_altas = cria_dict(df_altas_baixas_concat)
    maiores_baixas = cria_dict(df_altas_baixas_concat, True)

    acoes_em_alta_baixa = {
        "alta": maiores_altas,
        "baixa": maiores_baixas,
    }

    return acoes_em_alta_baixa

def convert_to_float(valor: str) -> float:
    """Converte as colunas "Valor" dos dataframes para float.

    ### Argumentos:
    - valor (str): Dataframe a ser convertido

    ### Returns:
    - float: Valor convertido para float
    """

    if isinstance(valor, str):
        valor_limpo = valor.replace('+', '').replace('%', '').replace(".", "").replace(',', '.')

        return -float(valor_limpo.replace("-", "")) if '-' in valor else float(valor_limpo)

    return np.nan

def cria_dict(dataframe: pd.DataFrame, ascending: bool = False) -> dict:
    """Tranforma DataFrames em dicionário.

    # Argumentos:
    - dataframe (pd.DataFrame): DataFrame a ser convertido
    - ascending (bool, optional): Ordem de classificação. Por padrão, False.

    # Returns:
    - dict: Dicionário com os dados do DataFrame
    """

    return (
        dataframe
        .sort_values(
            by="Variação",
            ascending = ascending
        )
        .reset_index(drop = True)
        .loc[:1]
        .to_dict(orient = "records")
    )

if __name__ == "__main__":
    print(extrai_dados())
