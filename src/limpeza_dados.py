"""
Módulo de transformação e limpeza de dados para o projeto de internações por AVC.

Este script realiza a transformação dos dados brutos extraídos do DATASUS para um formato
"Silver" mais limpo e estruturado, adequado para análises e visualizações posteriores.

Processos realizados:
- Filtragem de linhas válidas (apenas municípios com código IBGE)
- Limpeza e conversão de colunas numéricas (remoção de separadores, tratamento de valores ausentes)
- Separação de código IBGE e nome do município
- Reorganização de colunas para melhor usabilidade
- Salvamento em formato CSV otimizado

Dependências:
- pandas: Manipulação de dados e DataFrames
- numpy: Suporte para operações numéricas (não usado diretamente, mas importado)
- log: Logger customizado

Uso:
    from tratamento import transform_to_silver
    transform_to_silver('dados_brutos.csv', 'dados_silver.csv')
"""

import pandas as pd
import numpy as np
import os
from log import logger


# Caminho para a raiz do projeto
project_root = os.path.dirname(os.path.dirname(__file__))


def transform_to_silver(input_path, output_path):
    """
    Transforma dados brutos do DATASUS em formato Silver limpo.

    Esta função processa o CSV bruto extraído do TABNET, aplicando limpeza e
    estruturação para preparar os dados para análises posteriores.

    Args:
        input_path (str): Caminho para o arquivo CSV bruto de entrada.
        output_path (str): Caminho para salvar o arquivo CSV Silver de saída.

    Returns:
        None: Salva o arquivo processado no caminho especificado.

    Raises:
        Exception: Em caso de erro na leitura, processamento ou salvamento dos dados.

    Notas:
        - Filtra apenas linhas de municípios válidos (código IBGE de 6 dígitos)
        - Converte valores numéricos, tratando separadores e valores ausentes
        - Separa código IBGE e nome do município em colunas distintas
        - Reorganiza colunas para melhor usabilidade
    """
    try:
        logger.info(f"Iniciando transformação Silver do arquivo: {input_path}")

        # 1. Carregar os dados brutos
        df = pd.read_csv(input_path, encoding="utf-8-sig")

        # 2. Remover linhas de "Total" ou notas de rodapé que o DATASUS costuma colocar
        # Filtra apenas linhas que começam com o código IBGE (6 dígitos)
        df = df[df["municipio"].str.contains(r"^\d{6}", na=False)].copy()

        # 3. Limpeza das colunas de data (substituir '-' por '0' e converter para int)
        # Identificamos as colunas de data (que não são a 'municipio')
        data_cols = [c for c in df.columns if c != "municipio"]

        for col in data_cols:
            # Remove pontos de milhar se existirem, troca '-' por '0' e converte
            df[col] = df[col].astype(str).str.replace(".", "", regex=False)
            df[col] = df[col].replace("-", "0").replace("", "0")
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        # 4. Separar Código IBGE e Nome do Município para facilitar filtros
        # O padrão é "330010 ANGRA DOS REIS"
        df["municipio_id"] = df["municipio"].str.extract(r"^(\d{6})")
        df["municipio_nome"] = df["municipio"].str.extract(r"^\d{6}\s+(.*)")

        # 5. Reorganizar colunas (ID e Nome na frente)
        cols_final = ["municipio_id", "municipio_nome"] + data_cols
        df_silver = df[cols_final]

        # 6. Salvar versão Silver
        df_silver.to_csv(output_path, index=False, encoding="utf-8-sig")

        logger.info(f"Arquivo Silver gerado com sucesso: {output_path}")
        logger.info(f"Total de municípios processados: {len(df_silver)}")

    except Exception as e:
        logger.error(f"Erro na transformação Silver: {str(e)}")


# Execução
if __name__ == "__main__":
    input_file = os.path.join(project_root, "data", "raw", "internacoes_avc_rj.csv")
    output_file = os.path.join(
        project_root, "data", "processed", "internacoes_avc_rj_silver.csv"
    )
    transform_to_silver(input_file, output_file)
