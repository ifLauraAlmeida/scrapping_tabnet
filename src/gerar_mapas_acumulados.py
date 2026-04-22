"""
Módulo para geração de mapas mensais de internações por AVC no Rio de Janeiro.

Este script processa dados de internações hospitalares por acidente vascular cerebral (AVC)
 e gera uma série de mapas de calor (heatmaps) que mostram a taxa mensal por município,
 com escala de cores fixa para permitir comparação entre meses.

Funcionalidades:
- Carrega dados de CSV processado
- Obtém dados populacionais do IBGE (Censo 2022)
- Baixa malha geográfica do estado do Rio de Janeiro
- Gera mapas mensais sem acumulação histórica

Dependências:
- pandas: Manipulação de dados
- geopandas: Manipulação de dados geoespaciais
- requests: Requisições HTTP para APIs
- matplotlib: Geração de gráficos
- io: Manipulação de streams binários
- os: Operações do sistema de arquivos
- log: Logger customizado

Uso:
    from evolucao import gerar_serie_acumulativa_perfeita
    gerar_serie_acumulativa_perfeita('dados.csv')
"""

import pandas as pd
import geopandas as gpd
import requests
import matplotlib.pyplot as plt
import io
import os
from log import logger


# Caminho para a raiz do projeto
project_root = os.path.dirname(os.path.dirname(__file__))


def gerar_serie_mensal(csv_path):
    """
    Gera uma série de mapas de calor mensais de internações por AVC.

    Esta função processa dados de internações hospitalares por município no Rio de Janeiro,
    calcula taxas mensais por 100.000 habitantes e gera mapas mensais com escala de cores
    fixa para permitir comparação entre meses.

    Args:
        csv_path (str): Caminho para o arquivo CSV contendo os dados de internações.
                        O CSV deve ter uma coluna 'municipio_id' e colunas de datas no formato 'YYYY/MMM'.

    Returns:
        None: Salva os mapas como arquivos PNG na pasta 'mapas_avc'.

    Raises:
        Exception: Em caso de erro na leitura de dados, requisições HTTP ou geração de mapas.

    Notas:
        - Utiliza dados populacionais do Censo 2022 do IBGE
        - Baixa malha geográfica do IBGE para o estado do RJ
        - Escala de cores é travada no máximo histórico mensal para comparação justa
        - Processa os dados mês a mês, sem acumular valores anteriores
    """
    try:
        # 1. Configuração de Pastas
        PASTA = os.path.join(project_root, "data", "mapas_avc")
        if not os.path.exists(PASTA):
            os.makedirs(PASTA)
            logger.info(f"Pasta {PASTA} criada.")

        # 2. Carga de Dados e População
        df_silver = pd.read_csv(csv_path, dtype={"municipio_id": str})

        logger.info("Buscando base populacional fixa (Censo 2022)...")
        url_pop = "https://servicodados.ibge.gov.br/api/v3/agregados/4709/periodos/2022/variaveis/93?localidades=N6[N3[33]]"
        res_pop = requests.get(url_pop).json()
        pop_dict = {
            item["localidade"]["id"][:6]: int(item["serie"]["2022"])
            for item in res_pop[0]["resultados"][0]["series"]
        }

        # 3. Identificar Colunas e Calcular VMAX (Teto da escala)
        MESES_MAP = {
            "Jan": "01",
            "Fev": "02",
            "Mar": "03",
            "Abr": "04",
            "Mai": "05",
            "Jun": "06",
            "Jul": "07",
            "Ago": "08",
            "Set": "09",
            "Out": "10",
            "Nov": "11",
            "Dez": "12",
        }

        colunas = [c for c in df_silver.columns if "/" in c]
        colunas.sort(
            key=lambda x: (int(x.split("/")[0]), MESES_MAP.get(x.split("/")[1]))
        )

        # Calcula a maior taxa mensal histórica para travar a escala
        pop_series = df_silver["municipio_id"].map(pop_dict)
        taxas_mensais = df_silver[colunas].div(pop_series, axis=0) * 100000
        VMAX_FIXO = taxas_mensais.max().max()
        logger.info(f"O teto máximo mensal é: {VMAX_FIXO:.2f}. Travando escala...")

        # 4. Download do Mapa (FORA DO LOOP)
        logger.info("Baixando malha geográfica do Rio de Janeiro...")
        url_mapa = "https://servicodados.ibge.gov.br/api/v3/malhas/estados/33?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=municipio"
        response = requests.get(url_mapa)
        response.raise_for_status()
        rj_map = gpd.read_file(io.BytesIO(response.content))
        rj_map["municipio_id_6"] = rj_map["codarea"].str[:6]

        logger.info(f"Iniciando plotagem de {len(colunas)} meses...")
        for i, data_ref in enumerate(colunas):
            ano, mes_nome = data_ref.split("/")
            mes_num = MESES_MAP.get(mes_nome, "00")

            taxas_mensais_municipio = (
                df_silver[data_ref].astype(float) / pop_series
            ) * 100000

            df_temp = pd.DataFrame(
                {
                    "municipio_id": df_silver["municipio_id"],
                    "taxa_mensal": taxas_mensais_municipio,
                }
            )

            merged = rj_map.merge(
                df_temp, left_on="municipio_id_6", right_on="municipio_id"
            )

            fig, ax = plt.subplots(1, 1, figsize=(15, 10), dpi=100)
            merged.plot(
                column="taxa_mensal",
                ax=ax,
                cmap="YlOrRd",
                vmin=0,
                vmax=VMAX_FIXO,
                legend=True,
                edgecolor="black",
                linewidth=0.2,
                legend_kwds={
                    "label": "Taxa Mensal por 100k hab.",
                    "orientation": "horizontal",
                    "pad": 0.02,
                },
            )

            plt.title(
                f"Taxa Mensal de AVC no RJ: {data_ref}",
                fontsize=20,
                fontweight="bold",
            )
            ax.set_axis_off()

            nome_arq = f"{PASTA}/heatmap_{ano}_{mes_num}_{mes_nome}.png"
            plt.savefig(nome_arq, bbox_inches="tight", pad_inches=0.1)
            plt.close(fig)

            if (i + 1) % 24 == 0:
                logger.info(f"Processado: {data_ref}")

        logger.info(f"Sucesso! {len(colunas)} imagens salvas em {PASTA}.")

    except Exception as e:
        logger.error(f"Erro crítico: {e}")
        import traceback

        logger.error(traceback.format_exc())


if __name__ == "__main__":
    csv_path = os.path.join(
        project_root, "data", "processed", "internacoes_avc_rj_silver.csv"
    )
    gerar_serie_mensal(csv_path)
