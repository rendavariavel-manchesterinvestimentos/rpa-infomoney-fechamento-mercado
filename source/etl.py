"""Extrai dados dos ativos principais e dos ativos em alta e baixapara o fechamento
do mercado direto do site Yahoo Finance e formata deixando em formato de Dicionário"""

import time
import logging
import pandas as pd
import numpy as np
import pandera as pa

from pandera import Column, DataFrameSchema, Check

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


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

def extrai_ativos_principais(url: str, nome_ativo: str) -> pd.DataFrame:
    """
    Extrai os ativos principais de uma página de ativos.

    ### Argumentos:
    - url: URL da página de ativos
    - nome_ativo: Nome do ativo

    ### Returns:
    - DataFrame com os ativos principais
    """

    options = Options()
    options.add_argument("--log-level=3")
    browser = webdriver.Chrome(options=options)
    time.sleep(5)
    browser.get(url)


    nome_atual = browser.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[1]/div/div/section/h1').text
    time.sleep(1)
    nome_atual = nome_ativo
    valor_atual = browser.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section/div[1]/fin-streamer[1]/span').text
    time.sleep(1)
    variacao_percentual = browser.find_element(By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section[1]/div[2]/div[1]/section/div/section/div[1]/fin-streamer[3]/span').text
    variacao_percentual = variacao_percentual.replace("(", " ").replace(")", " ").strip()

    data = {
        'Símbolo': [nome_atual],
        'Último Preço': [valor_atual],
        '% de var.': [variacao_percentual]
    }

    df_ativos_principais = pd.DataFrame(data)

    browser.quit()

    return df_ativos_principais

def obter_variacao_ativos() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Obtem os dados de Variação dos ativos principais e dos ativos em alta e baixa

    ### Returns:
    - df_ativos_principais (pd.DataFrame): DataFrame com dados de Variação dos ativos principais
    - df_altas_baixas_concat (pd.DataFrame): DataFrame com dados de Variação dos ativos em alta e baixa
    """

    options = Options()
    options.add_argument("--log-level=3")
    browser = webdriver.Chrome(options = options)

    # Extrai os ativos principais
    df_ibov = extrai_ativos_principais("https://finance.yahoo.com/quote/%5EBVSP/", "^BVSP")
    time.sleep(1)
    df_sep = extrai_ativos_principais("https://finance.yahoo.com/quote/%5EGSPC/", "^GSPC")
    time.sleep(1)
    df_euro = extrai_ativos_principais("https://finance.yahoo.com/quote/LYMZ.DE/", "LYMZ.DE")
    time.sleep(1)
    df_dolar = extrai_ativos_principais("https://finance.yahoo.com/quote/BRL=X/", "BRL=X")
    time.sleep(1)
    df_nasdaq = extrai_ativos_principais("https://finance.yahoo.com/quote/%5EIXIC/", "^IXIC")

    # Concatena os DataFrames
    df_ativos_principais = pd.concat([df_ibov, df_sep, df_euro, df_dolar, df_nasdaq])

    # Extrai as maiores e menores variações
    browser.get("https://www.infomoney.com.br/ferramentas/altas-e-baixas/")
    time.sleep(10)
    df_maiores_menores_variacoes = pd.read_html(browser.page_source, decimal=",")[0]

    # Formata a coluna 'Var. Dia (%)' para incluir vírgulas como separador decimal e duas casas decimais
    df_maiores_menores_variacoes["Var. Dia (%)"] = (
        (df_maiores_menores_variacoes["Var. Dia (%)"].astype(float) / 100)
        .map("{:,.2f}%".format)
        .str.replace('.', ',')
    )

    df_maiores_menores_variacoes["Último (R$)"] = (
        (df_maiores_menores_variacoes["Último (R$)"].astype(float) / 100)
        .map("{:,.2f}%".format)
        .str.replace('.', ',')
    )

    # Pega as colunas que desejamos usar
    colunas_desejadas = ["Ativo", "Último (R$)", "Var. Dia (%)"]
    df_maiores_menores_variacoes = df_maiores_menores_variacoes[colunas_desejadas]

    # Coloca em ordem crescente
    df_maiores_menores_variacoes = df_maiores_menores_variacoes.sort_index()

    browser.quit()

    return df_ativos_principais, df_maiores_menores_variacoes

def formata_df_ativos_principais(df_ativos_principais: pd.DataFrame) -> dict:
    """
    Formata o dataframe dos ativos principais e transforma em dicionário.

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

    df_ativos_principais["Variação"] = df_ativos_principais["Variação"].apply(convert_to_float) / 100

    # Formata a coluna Valor e tranforma em float
    df_ativos_principais["Valor"] = df_ativos_principais["Valor"].apply(convert_to_float).round(3)


    df_ativos_principais = df_ativos_principais.astype(
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
                pa.String,
                nullable = False,
                checks = Check.isin(["^GSPC", "^IXIC", "LYMZ.DE", "BRL=X", "^BVSP"])
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

def formata_df_altas_baixas_concat(df_maiores_menores_variacoes: pd.DataFrame) -> dict:
    """Formata o dataframe dos ativos em alta e em baixa e transforma em dicionário.

    ### Argumentos:
    - df_maiores_menores_variacoes (pd.DataFrame): DataFrame com dados dos ativos principais

    ### Returns:
    - acoes_em_alta_baixa (dict): Dicionário com os dados dos ativos principais
    """

    #Renomeia o dataframe
    df_maiores_menores_variacoes.rename(
        columns={
            'Ativo': 'Ticker',
            'Último (R$)': 'Valor',
            'Var. Dia (%)': 'Variação',
        },
        inplace = True
    )

    # Maiores e Menores Variações
    df_maiores_menores_variacoes = df_maiores_menores_variacoes.reindex(
        columns = ['Ticker', 'Valor', 'Variação'],
    )

    # Transforma em float
    df_maiores_menores_variacoes["Variação"] = df_maiores_menores_variacoes["Variação"].apply(convert_to_float)
    df_maiores_menores_variacoes["Valor"] = df_maiores_menores_variacoes["Valor"].apply(convert_to_float)

    df_maiores_menores_variacoes = df_maiores_menores_variacoes.astype(
        dtype = {
            "Ticker": str,
            "Valor": float,
            "Variação": float,
        }
    )

    # Cria dicionário df cotação concatenado
    maiores_altas = cria_dict(df_maiores_menores_variacoes)
    maiores_baixas = cria_dict(df_maiores_menores_variacoes, True)

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

        return float(valor_limpo)

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
